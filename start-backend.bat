@echo off
setlocal
title SPSSGO Backend (FastAPI :8000)
cd /d "%~dp0"
if not defined APP_ENV set APP_ENV=development
if not defined ALLOW_INSECURE_DEV_DEFAULTS set ALLOW_INSECURE_DEV_DEFAULTS=1
if not defined DB_AUTO_CREATE set DB_AUTO_CREATE=1
if not defined JOB_BACKEND set JOB_BACKEND=local
if not defined MYSQL_HOST set MYSQL_HOST=127.0.0.1
if not defined MYSQL_PORT set MYSQL_PORT=3306
if not defined MYSQL_USER set MYSQL_USER=root
if not defined MYSQL_PASSWORD set MYSQL_PASSWORD=facai888
if not defined MYSQL_DATABASE set MYSQL_DATABASE=data_analysis
if not defined ADMIN_USERNAME set ADMIN_USERNAME=admin
if not defined ADMIN_PASSWORD set ADMIN_PASSWORD=spssgo2024
if not defined ADMIN_SECRET_KEY set ADMIN_SECRET_KEY=dev-admin-secret-key-local-only
if not defined R_ENABLED set R_ENABLED=1
if not defined RSCRIPT_BIN set "RSCRIPT_BIN=C:\Program Files\R\R-4.5.3\bin\Rscript.exe"
if not defined R_LIBS_USER set "R_LIBS_USER=%APPDATA%\R\win-library\4.5"
if not exist "%~dp0.tmp\rtemp" mkdir "%~dp0.tmp\rtemp"
if not defined R_TEMP_DIR set "R_TEMP_DIR=%~dp0.tmp\rtemp"
set "BACKEND_LOG_MAX_BYTES=10485760"
for %%F in ("%~dp0.tmp\backend*.log") do (
    if exist "%%~fF" (
        if %%~zF GEQ %BACKEND_LOG_MAX_BYTES% move /Y "%%~fF" "%%~fF.old" >nul
    )
)
set "BACKEND_MODE=stable"
if "%BACKEND_RELOAD%"=="1" (
    set "BACKEND_MODE=dev-restart"
)
echo ========================================
echo   Starting backend service...
echo   Mode: %BACKEND_MODE%
echo   URL: http://localhost:8000
echo   Press Ctrl+C to stop
echo ========================================
if "%BACKEND_RELOAD%"=="1" (
    python scripts\run_backend_dev.py
) else (
    python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
)
pause
