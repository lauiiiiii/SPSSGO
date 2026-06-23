@echo off
title SPSSGO - Build Frontend
cd /d "%~dp0..\spssgo_frontend"
if errorlevel 1 (
    echo [ERROR] cannot cd into "%~dp0..\spssgo_frontend"
    echo Check whether the spssgo_frontend folder exists next to spssgo.
    pause
    exit /b 1
)

echo ============================================================
echo   [1] Build Frontend (da bao qian duan)
echo ------------------------------------------------------------
echo   What: compile spssgo_frontend/src into spssgo_frontend/dist,
echo         then copy to spssgo/frontend/dist for production serving
echo   When to use:
echo     - First time deployment
echo     - After you changed any frontend code
echo   Next step after this: run 2-sheng chan mo shi qi dong.bat
echo ============================================================
echo.

where node >nul 2>&1
if errorlevel 1 (
    echo [ERROR] node.exe not found in PATH.
    echo Please install Node.js from https://nodejs.org/ first.
    pause
    exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm not found in PATH.
    echo Please reinstall Node.js or fix your PATH.
    pause
    exit /b 1
)

echo Node version:
call node -v
echo npm version:
call npm -v
echo.

if not exist "node_modules" (
    echo node_modules not found, running npm install ...
    call npm install
    if errorlevel 1 (
        echo.
        echo [ERROR] npm install failed. See messages above.
        pause
        exit /b 1
    )
)

echo Running npm run build ...
call npm run build
if errorlevel 1 (
    echo.
    echo [ERROR] npm run build failed. See messages above.
    pause
    exit /b 1
)

echo.
echo Copying build output to spssgo\frontend\dist ...
if exist "%~dp0frontend\dist" rmdir /s /q "%~dp0frontend\dist"
xcopy /E /I /Y "%~dp0..\spssgo_frontend\dist\*" "%~dp0frontend\dist\"
if errorlevel 1 (
    echo.
    echo [ERROR] failed to copy dist to spssgo\frontend\dist
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Build succeeded. Files are in spssgo\frontend\dist
echo ============================================================
pause
exit /b 0
