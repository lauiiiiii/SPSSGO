@echo off
title SPSSGO - Dev Start
cd /d "%~dp0"

echo ============================================================
echo   [3] Dev Start (kai fa mo shi qi dong)
echo ------------------------------------------------------------
echo   What: backend (port 8000) + vite dev server (port 5577)
echo         frontend hot reload, for local coding only
echo   When to use:
echo     - You are editing frontend / backend code
echo     - You need hot reload
echo   Notes:
echo     - SLOW first paint, NOT suitable for real users
echo     - Production users should use option 2 instead
echo ============================================================
echo.

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

echo Starting backend on :8000 ...
start "SPSSGO Backend Dev" cmd /k "cd /d %~dp0 && python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload --reload-include *.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo Starting vite dev server on :5577 ...
start "SPSSGO Frontend Dev" cmd /k "cd /d %~dp0..\spssgo_frontend && npm run dev"

echo.
echo Both windows launched.
echo   Backend:  http://127.0.0.1:8000
echo   Frontend: http://127.0.0.1:5577
echo.
pause
