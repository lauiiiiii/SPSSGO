@echo off
title SPSSGO - Build Frontend (GitHub)
cd /d "%~dp0..\spssgo_frontend"

echo ============================================================
echo   Building frontend (GitHub / workspace mode)...
echo ============================================================
echo.

call npm install
if %errorlevel% neq 0 (
    echo [ERROR] npm install failed
    pause
    exit /b 1
)

call npm run build:workspace
if %errorlevel% neq 0 (
    echo [ERROR] npm run build:workspace failed
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Copying dist to SPSSGO\frontend\dist...
echo ============================================================
echo.

set "TARGET=%~dp0..\SPSSGO\frontend\dist"
if exist "%TARGET%" rmdir /s /q "%TARGET%"
xcopy /E /I /Y "dist\*" "%TARGET%"

echo.
echo [OK] Done. Backend can now serve the latest frontend build.
echo.
pause
