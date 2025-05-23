@echo off
cd /d C:\Users\hp\Desktop\Diabetic-Predictor-main\Diabetic-Predictor-main

REM React Frontend
start cmd /k "cd front-end && npm start"

REM Node.js Backend
start cmd /k "cd node.js-service && node server.js"

REM Prisma Studio
start cmd /k "cd node.js-service && npx prisma studio"

REM Python Backend
start cmd /k "cd python-service && python app.py"

echo 🚀 All services started in separate terminals.
pause
