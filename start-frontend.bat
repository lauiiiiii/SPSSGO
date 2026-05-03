@echo off
setlocal
title SPSSGO Frontend (Vite :5577)
cd /d "%~dp0frontend"
echo ========================================
echo   Starting frontend service...
echo   URL: http://localhost:5577
echo   Backend API should be running on: http://127.0.0.1:8000
echo   Tip: start backend first or use start-all.bat
echo   Press Ctrl+C to stop
echo ========================================
npm run dev
pause
