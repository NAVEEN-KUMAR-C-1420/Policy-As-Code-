"""
Code Integrity & Safe Mode Engine
=================================
Reads the deployed manifest.json and compares canonical hashes
of deployed YAML files to ensure runtime integrity.

If a file has been tampered with:
  - System enters SAFE MODE
  - Pipeline execution is BLOCKED
  - Drift Detected is raised
  - Frontend displays Integrity Failed alert with detailed diagnostic information.
"""

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

from core.paths import AGENTS_DIR, MIDDLEWARE_DIR
from core.paths import BASE_DIR as PROJECT_ROOT

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

_STARTUP_INTEGRITY_CACHE = None

# Import our new canonical yaml hasher (needs to be available in path)
try:
    from scripts.utils.yaml_canonicalizer import get_yaml_hash
except ImportError:
    # Fallback if running from a different context
    sys.path.insert(0, str(PROJECT_ROOT.parent))
    from scripts.utils.yaml_canonicalizer import get_yaml_hash

_SAFE_MODE_OVERRIDE = False


def set_safe_mode_override(enabled: bool):
    """Allows manual simulation of Safe Mode via Demo/Settings endpoint."""
    global _SAFE_MODE_OVERRIDE
    _SAFE_MODE_OVERRIDE = enabled


def load_manifest() -> dict:
    """Loads the immutable manifest generated during CI/CD."""
    manifest_path = PROJECT_ROOT.parent / "manifest.json"
    if not manifest_path.exists():
        return None
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def verify_system_integrity() -> dict[str, Any]:
    """
    Verifies runtime hashes against the local manifest.json.
    Returns integrity status dict.
    """
    global _SAFE_MODE_OVERRIDE

    manifest = load_manifest()
    
    # We still fetch git commit for diagnostic purposes, though manifest has it.
    git_commit = "head"
    try:
        import subprocess
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=str(PROJECT_ROOT), stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        pass

    if _SAFE_MODE_OVERRIDE:
        return {
            "status": "FAILED",
            "safe_mode": True,
            "reason": "Safe Mode manually simulated via Developer Settings for demonstration.",
            "mismatches": ["SIMULATED"],
            "commit_sha": git_commit,
            "deployment_version": manifest.get("version", "1") if manifest else "1",
            "required_action": "Disable Safe Mode simulation in Developer Settings.",
        }

    if not manifest:
        # If there is no manifest, we assume local dev or a system that hasn't been through the CI pipeline.
        return {
            "status": "PASSED",
            "safe_mode": False,
            "reason": "No manifest.json found. Bypassing strict runtime integrity.",
            "commit_sha": git_commit,
            "deployment_version": "dev",
            "required_action": "None",
        }

    if manifest.get("validation_status") != "PASSED":
        return {
            "status": "FAILED",
            "safe_mode": True,
            "reason": "Manifest indicates governance validation failed during CI/CD.",
            "mismatches": ["manifest.validation_status != PASSED"],
            "commit_sha": git_commit,
            "deployment_version": manifest.get("version", "unknown"),
            "required_action": "Do not deploy builds that fail governance validation.",
        }

    expected_hashes = manifest.get("yaml_hashes", {})
    mismatches = []
    
    # Check all files that were validated and hashed in the manifest
    for rel_path, expected_hash in expected_hashes.items():
        full_path = PROJECT_ROOT / rel_path
        if full_path.exists():
            try:
                # Use canonical yaml hash
                actual_hash = get_yaml_hash(full_path)
                if actual_hash != expected_hash:
                    mismatches.append(f"Drift detected in {rel_path}: actual hash {actual_hash[:8]} != expected {expected_hash[:8]}")
            except Exception as e:
                mismatches.append(f"Error hashing {rel_path}: {e}")
        else:
            mismatches.append(f"Missing governed file: {rel_path}")

    # Recompute combined hash for overall integrity
    runtime_yaml_hashes = []
    for rel_path in expected_hashes.keys():
        full_path = PROJECT_ROOT / rel_path
        if full_path.exists():
            try:
                runtime_yaml_hashes.append(get_yaml_hash(full_path))
            except Exception:
                pass
    
    runtime_combined = "".join(sorted(runtime_yaml_hashes))
    actual_combined_hash = hashlib.sha256(runtime_combined.encode('utf-8')).hexdigest()
    
    if actual_combined_hash != manifest.get("combined_hash") and not mismatches:
        mismatches.append("Combined hash mismatch indicating overall configuration drift.")

    if mismatches:
        reason_str = "; ".join(mismatches)
        return {
            "status": "FAILED",
            "safe_mode": True,
            "reason": f"Integrity check failed: {reason_str}",
            "mismatches": mismatches,
            "commit_sha": git_commit,
            "deployment_version": manifest.get("version", "unknown"),
            "required_action": "Revert uncommitted code changes or re-run deployment pipeline.",
        }

    return {
        "status": "PASSED",
        "safe_mode": False,
        "reason": "All runtime hashes match the deployed manifest.",
        "commit_sha": git_commit,
        "deployment_version": manifest.get("version", "unknown"),
        "required_action": "None",
    }

def run_startup_integrity_check():
    """Runs the integrity check on startup and caches the result globally."""
    global _STARTUP_INTEGRITY_CACHE
    _STARTUP_INTEGRITY_CACHE = verify_system_integrity()
    if _STARTUP_INTEGRITY_CACHE.get("safe_mode"):
        logging.critical(
            f"CRITICAL: Code Integrity Verification Failed during startup! "
            f"System is entering SAFE MODE. Reason: {_STARTUP_INTEGRITY_CACHE.get('reason')}"
        )
    else:
        logging.info("Code Integrity Verification Passed on startup.")

class IntegrityEnforcementMiddleware(BaseHTTPMiddleware):
    """
    Middleware that blocks execution routes if the system is in safe mode.
    Diagnostic endpoints remain accessible.
    """
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # We only block execution endpoints. We allow /docs, /health, /integrity, etc.
        if path.startswith("/agents") or path.startswith("/pipeline"):
            
            if _SAFE_MODE_OVERRIDE:
                integrity = verify_system_integrity()
            else:
                integrity = _STARTUP_INTEGRITY_CACHE or verify_system_integrity()
                
            if integrity.get("safe_mode"):
                return JSONResponse(
                    status_code=403,
                    content={
                        "success": False, 
                        "message": "System is in SAFE MODE due to integrity violation. Execution blocked.",
                        "reason": integrity.get("reason", "Unknown integrity failure"),
                        "mismatches": integrity.get("mismatches", [])
                    }
                )
                
        return await call_next(request)
