cd /d "%~dp0..\spssgo_frontend"
call npm install && call npm run build:workspace && if exist "%~dp0frontend\dist" rmdir /s /q "%~dp0frontend\dist" && xcopy /E /I /Y "dist\*" "%~dp0frontend\dist"
pause