import os
import sys
import json
import datetime
import traceback
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add backend directory to sys path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from scripts.utils.yaml_canonicalizer import canonicalize_yaml, get_yaml_hash
from scripts.utils.ast_analyzer import extract_agent_metadata
from app.middleware.agent_policy_compat import validate_agent_policy_compat
# FIX 1: Import schema validator so it runs in every CI execution
from app.middleware.policy_validator import validate_policy
import yaml

def print_error(msg: str):
    print(f"❌ FAIL: {msg}")

def print_success(msg: str):
    print(f"✅ OK: {msg}")

def run_governance_validation():
    print("\n==================================================")
    print(" GOVERNANCE VALIDATION (CI/CD)")
    print("==================================================\n")

    agents_dir = backend_dir / "app" / "agents"
    if not agents_dir.exists():
        print_error("Agents directory not found.")
        sys.exit(1)

    manifest = {
        "version": "1.0",
        "commit_id": os.environ.get("GITHUB_SHA", "local-dev"),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "yaml_hashes": {},
        "combined_hash": "",
        "validated_files": [],
        "build_number": os.environ.get("GITHUB_RUN_NUMBER", "local-1"),
        "branch": os.environ.get("GITHUB_REF_NAME", "local-branch"),
        "validation_status": "PENDING"
    }

    # FIX 2: Track overall pipeline state separately from per-agent state.
    # any_agent_failed accumulates across all agents; agent_validation_failed
    # is reset on every iteration so one agent's failure cannot poison another.
    any_agent_failed = False

    agent_dirs = [d for d in agents_dir.iterdir() if d.is_dir() and d.name != "__pycache__"]

    for agent_dir in agent_dirs:
        print(f"\n--- Validating Agent: {agent_dir.name} ---")

        # FIX 2: Per-agent flag — reset on every loop iteration.
        agent_validation_failed = False

        agent_yaml_path = agent_dir / "agent.yaml"
        policy_yaml_path = agent_dir / "policy.yaml"

        if not agent_yaml_path.exists() or not policy_yaml_path.exists():
            print_error(f"Missing agent.yaml or policy.yaml in {agent_dir.name}")
            any_agent_failed = True
            continue

        try:
            with open(agent_yaml_path, "r", encoding="utf-8") as f:
                agent_config = yaml.safe_load(f)
            with open(policy_yaml_path, "r", encoding="utf-8") as f:
                policy_config = yaml.safe_load(f)
        except Exception as e:
            print_error(f"Failed to parse YAML in {agent_dir.name}: {e}")
            any_agent_failed = True
            continue

        # ── FIX 1: Policy schema validation ────────────────────────────────────
        # validate_policy() enforces the full governance schema (hitl, guardrails,
        # data_retention, regulatory_frameworks, etc.) BEFORE any compatibility
        # check.  A malformed policy.yaml must never reach deployment.
        policy_schema_result = validate_policy(policy_config, raise_on_error=False)
        if not policy_schema_result.valid:
            print_error(f"Policy schema validation failed for {agent_dir.name}:")
            for err in policy_schema_result.errors:
                print(f"  - {err}")
            agent_validation_failed = True
            any_agent_failed = True
            # Skip compatibility check — policy schema is malformed.
            continue

        # 1. AST Analysis
        metadata = extract_agent_metadata(str(agent_dir))

        # 2. Compare AST against agent.yaml
        code_tools = set(metadata.get("tools", []))
        yaml_tools = set(agent_config.get("tools", []))

        # Every tool declared in agent.yaml must exist in code
        missing_in_code = yaml_tools - code_tools
        if missing_in_code:
            # Our AST looks for StructuredTool.from_function(..., name="...") and
            # @tool-decorated functions, which covers all standard registration patterns.
            print_error(f"Tools declared in agent.yaml but missing in code: {missing_in_code}")
            agent_validation_failed = True
            any_agent_failed = True

        # Every tool implemented in code must be in agent.yaml
        undeclared_in_yaml = code_tools - yaml_tools
        if undeclared_in_yaml:
            print_error(f"Tools found in code but not declared in agent.yaml: {undeclared_in_yaml}")
            agent_validation_failed = True
            any_agent_failed = True

        # ── FIX 3: Model mismatch now fails CI ─────────────────────────────────
        # Previously this was a warning-only check with validation_failed commented
        # out.  A model declared in agent.yaml that differs from what the code
        # actually instantiates is a governance violation and must block deployment.
        code_models = set(metadata.get("models", []))
        yaml_model = agent_config.get("model")
        if yaml_model and code_models and yaml_model not in code_models:
            print_error(
                f"Model mismatch for {agent_dir.name}: "
                f"agent.yaml declares '{yaml_model}' but code instantiates: {sorted(code_models)}"
            )
            agent_validation_failed = True
            any_agent_failed = True

        # 3. Compare agent.yaml against policy.yaml
        compat = validate_agent_policy_compat(agent_config, policy_config, raise_on_error=False)
        if not compat.valid:
            print_error(f"Policy mismatch for {agent_dir.name}:")
            for err in compat.errors:
                print(f"  - {err}")
            agent_validation_failed = True
            any_agent_failed = True

        # FIX 2: Branch on the per-agent flag, NOT the global accumulator.
        # This guarantees that a passing agent always gets its hashes written
        # regardless of whether a different agent failed earlier in the loop.
        if not agent_validation_failed:
            print_success(f"Agent '{agent_dir.name}' passed governance validation.")

            # 4. Generate Canonical Hashes
            agent_hash = get_yaml_hash(agent_yaml_path)
            policy_hash = get_yaml_hash(policy_yaml_path)

            # Store in manifest
            manifest["yaml_hashes"][f"agents/{agent_dir.name}/agent.yaml"] = agent_hash
            manifest["yaml_hashes"][f"agents/{agent_dir.name}/policy.yaml"] = policy_hash

            manifest["validated_files"].extend([
                f"agents/{agent_dir.name}/agent.yaml",
                f"agents/{agent_dir.name}/policy.yaml"
            ])
        else:
            print_error(f"Agent '{agent_dir.name}' FAILED governance validation — hashes not written.")

    # Include global config hashes if they exist
    config_dir = backend_dir / "app" / "config"
    if config_dir.exists():
        for yml_file in config_dir.glob("*.yaml"):
            h = get_yaml_hash(yml_file)
            manifest["yaml_hashes"][f"config/{yml_file.name}"] = h
            manifest["validated_files"].append(f"config/{yml_file.name}")

    if any_agent_failed:
        manifest["validation_status"] = "FAILED"
        print("\n==================================================")
        print("❌ GOVERNANCE VALIDATION FAILED")
        print("Deployment aborted.")
        print("==================================================\n")
        sys.exit(1)

    else:
        manifest["validation_status"] = "PASSED"

        # Compute combined hash
        import hashlib
        combined = "".join(sorted(manifest["yaml_hashes"].values()))
        manifest["combined_hash"] = hashlib.sha256(combined.encode('utf-8')).hexdigest()

        # Write manifest
        manifest_path = backend_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        print("\n==================================================")
        print("✅ GOVERNANCE VALIDATION PASSED")
        print(f"Manifest written to: {manifest_path}")
        print("Proceeding to deployment...")
        print("==================================================\n")
        sys.exit(0)


if __name__ == "__main__":
    run_governance_validation()
