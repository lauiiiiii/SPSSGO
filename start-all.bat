@echo off
setlocal
title SPSSGO Launcher
cd /d "%~dp0"

echo ========================================
echo   Starting SPSSGO services...
echo   Backend:  http://127.0.0.1:8000
echo   Frontend: http://localhost:5577
echo ========================================

start "SPSSGO Backend" cmd /c call "%~dp0start-backend.bat"

echo Waiting for backend to become ready...
set RETRIES=60

:wait_backend
powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/me' -UseBasicParsing -TimeoutSec 2 | Out-Null; exit 0 } catch { if ($_.Exception.Response) { exit 0 } else { exit 1 } }"
if %errorlevel%==0 goto start_frontend

set /a RETRIES-=1
if %RETRIES% LEQ 0 goto backend_timeout
timeout /t 1 /nobreak >nul
goto wait_backend

:start_frontend
echo Backend is ready. Starting frontend...
start "SPSSGO Frontend" cmd /c call "%~dp0start-frontend.bat"
echo Both service windows have been launched.
goto end

:backend_timeout
echo Backend did not respond within 60 seconds.
echo Frontend will still be started, but API requests may fail until backend is ready.
start "SPSSGO Frontend" cmd /c call "%~dp0start-frontend.bat"

:end
endlocal
