@echo off
REM ============================================================
REM  Arranca backend + frontend en ventanas separadas
REM ============================================================
setlocal
cd /d "%~dp0"

echo [1/2] Backend Django en http://127.0.0.1:8000
start "Analytics - Backend" cmd /k "%~dp0start-backend.cmd"

echo [2/2] Frontend Next.js en http://localhost:3000
start "Analytics - Frontend" cmd /k "%~dp0start-frontend.cmd"

echo.
echo Ambos servidores arrancando. Dashboard: http://localhost:3000
echo Cierra cada ventana para detener su servidor.