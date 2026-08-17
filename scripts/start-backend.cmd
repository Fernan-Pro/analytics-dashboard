@echo off
REM ============================================================
REM  Backend Django - servidor de desarrollo en :8000
REM  Requisito previo: Poetry instalado y `poetry install` hecho
REM ============================================================
setlocal
cd /d "%~dp0..\backend"

if not exist .env (
    echo [ERROR] No existe backend\.env
    echo         Copia backend\.env.example a backend\.env y completa los valores.
    exit /b 1
)

echo Iniciando Django en http://127.0.0.1:8000 ...
set PYTHONIOENCODING=utf-8
poetry run python manage.py runserver 127.0.0.1:8000