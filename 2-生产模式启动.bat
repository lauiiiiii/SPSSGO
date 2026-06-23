@echo off
setlocal
title SPSSGO - Production Start
cd /d "%~dp0"

set APP_ENV=production
set ALLOW_INSECURE_DEV_DEFAULTS=0
set BACKEND_RELOAD=0
set LOG_LEVEL=WARNING

if not defined DB_AUTO_CREATE set DB_AUTO_CREATE=0
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

if not exist "%~dp0frontend\dist\index.html" (
    echo.
    echo [WARN] frontend\dist\index.html not found.
    echo        Run 1-da bao qian duan.bat first, otherwise the homepage will 404.
    echo.
)

echo ============================================================
echo   [2] Production Start (sheng chan mo shi qi dong)
echo ------------------------------------------------------------
echo   What: start backend serving the pre-built frontend/dist
echo         same-origin, fast first paint, no extra proxy
echo   When to use:
echo     - Serving real users at spssgo.com
echo   Notes:
echo     - Make sure you ran 1-da bao qian duan.bat before this
echo     - Backend listens on port 5577 (same as frp default)
echo     - Do NOT close this window, closing it stops the site
echo ============================================================
echo.
echo   Local:  http://127.0.0.1:5577/
echo.

python -m uvicorn backend.app:app --host 0.0.0.0 --port 5577 --no-access-log --log-level warning

pause
endlocal
