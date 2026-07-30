"""
Policy Loader
==============
A tiny helper that reads an agent's policy.yaml file into a normal
Python dictionary so the tool interceptor can check rules against it.
"""

import yaml


def load_policy(policy_file_path):
    """Read a policy.yaml file and return its contents as a dictionary."""
    with open(policy_file_path, "r") as f:
        policy = yaml.safe_load(f)
    return policy
