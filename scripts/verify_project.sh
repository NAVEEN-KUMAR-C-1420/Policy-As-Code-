#!/bin/bash
cd "$(dirname "$0")/.."
python scripts/verify_project.py
if [ $? -ne 0 ]; then
    echo ""
    echo "[!] Verification failed. Please fix the issues and try again."
    exit 1
fi
echo ""
echo "[OK] Project is production-ready."
exit 0
