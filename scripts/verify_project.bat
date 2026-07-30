@echo off
setlocal
cd /d "%~dp0\.."
python scripts\verify_project.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] Verification failed. Please fix the issues and try again.
    exit /b %ERRORLEVEL%
)
echo.
echo [OK] Project is production-ready.
exit /b 0
