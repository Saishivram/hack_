@echo off
echo Starting MongoDB...
start mongod

echo Waiting for MongoDB to initialize...
timeout /t 5

echo Starting Backend Server...
cd backend
start python app.py

echo Starting Frontend Server...
cd ../frontend
start python server.py

echo.
echo Servers are running:
echo Frontend: http://localhost:3000
echo Backend: http://localhost:5000
echo.
echo You can now visit http://localhost:3000/register.html to create an account
pause 