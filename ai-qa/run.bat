@echo off
setlocal
cd /d "%~dp0"

echo ===================================================
echo     AI-QA GORILLADESK AUTOMATION RUNNER
echo ===================================================

if "%~1"=="" (
    echo Cach dung:
    echo   run.bat --test JOB-CREATE-001
    echo   run.bat --test OFFLINE-SYNC-001
    echo   run.bat --suite smoke
    echo   run.bat --suite module-job
    echo   run.bat --suite all-app-full-coverage
    echo.
    python orchestrator\main.py --help
    exit /b 0
)

python orchestrator\main.py %*
