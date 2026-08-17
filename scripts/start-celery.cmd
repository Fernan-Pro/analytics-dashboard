@echo off
REM ============================================================
REM  Celery worker + beat (scraping automatico)
REM  Requiere Redis corriendo en 127.0.0.1:6379
REM  Si no tienes Redis, usa scripts\fetch-data.cmd para
REM  poblar los datos manualmente sin Celery.
REM ============================================================
setlocal
cd /d "%~dp0..\backend"

if not exist .env (
    echo [ERROR] No existe backend\.env
    exit /b 1
)

REM --- Comprobar que Redis responde en el puerto 6379 ---
powershell -NoProfile -Command "$c = New-Object System.Net.Sockets.TcpClient; try { $c.Connect('127.0.0.1', 6379); $c.Close(); Write-Host 'Redis OK'; exit 0 } catch { exit 1 }"
if errorlevel 1 (
    echo.
    echo [ERROR] Redis no esta disponible en 127.0.0.1:6379
    echo.
    echo Opciones:
    echo   1^) docker compose up -d redis      ^(requiere Docker^)
    echo   2^) Instalar Memurai                ^(Redis para Windows^)
    echo   3^) Poblar datos sin Celery: scripts\fetch-data.cmd
    exit /b 1
)

echo Redis OK. Iniciando Celery worker + beat ...
set PYTHONIOENCODING=utf-8
start "Analytics - Celery worker" cmd /k "poetry run celery -A config worker -l info"
start "Analytics - Celery beat" cmd /k "poetry run celery -A config beat -l info"