# Local CI Verification Framework

This folder contains the **Single Source of Truth** for the project's CI verification logic. 

Instead of maintaining separate tests in GitHub Actions and local workflows, `verify_project.py` executes all environment validations, database checks, Pytest suites, Governance tests, and pipeline simulations in one place.

## How to use

Run the script before you commit:

```bash
# Windows
scripts\verify_project.bat

# Linux / Mac
./scripts/verify_project.sh
```

Or run Python directly:
```bash
python scripts/verify_project.py
```

## GitHub Actions Synchronization
The `.github/workflows/ci.yml` has been updated to simply execute `python scripts/verify_project.py`. This mathematically guarantees that if your local verification passes, GitHub Actions will pass.

## Git Pre-Commit Hook
You can enforce this by copying the `.git/hooks/pre-commit.example` into your `.git/hooks/pre-commit` file. This prevents broken code from being pushed to the repository.
