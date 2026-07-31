import hashlib
import json
from pathlib import Path
from typing import Any, Union
import yaml

def _canonicalize_value(val: Any) -> Any:
    """Recursively process values to ensure canonical sorting."""
    if isinstance(val, dict):
        # Sort dictionary keys recursively
        return {k: _canonicalize_value(val[k]) for k in sorted(val.keys())}
    elif isinstance(val, list):
        # Lists are preserved in order, but their elements are canonicalized
        return [_canonicalize_value(item) for item in val]
    return val

def canonicalize_yaml(filepath: Union[str, Path]) -> str:
    """
    Reads a YAML file, canonicalizes its structure (sorting keys, stripping comments/whitespace),
    and returns a canonical JSON string representation.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    if data is None:
        data = {}
        
    canonical_data = _canonicalize_value(data)
    # Serialize to JSON with sorted keys (just in case), no spaces for strict canonicalization
    return json.dumps(canonical_data, separators=(',', ':'), sort_keys=True)

def get_yaml_hash(filepath: Union[str, Path]) -> str:
    """Generates a SHA-256 hash of the canonicalized YAML."""
    canonical_str = canonicalize_yaml(filepath)
    return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
