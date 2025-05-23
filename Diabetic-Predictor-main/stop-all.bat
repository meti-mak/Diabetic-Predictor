@echo off
echo 🔴 Stopping all services...

REM Stop Node.js services
taskkill /F /IM node.exe >nul 2>&1

REM Stop Python services
taskkill /F /IM python.exe >nul 2>&1

REM OPTIONAL: Stop Prisma (uses electron sometimes)
taskkill /F /IM electron.exe >nul 2>&1

echo ✅ Node.js and Python services stopped.
pause
