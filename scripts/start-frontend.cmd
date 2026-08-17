@echo off
REM ============================================================
REM  Frontend Next.js - servidor de desarrollo en :3000
REM  Requisito previo: pnpm instalado y `pnpm install` hecho
REM ============================================================
setlocal
cd /d "%~dp0..\frontend"

if not exist .env.local (
    echo [INFO] Creando frontend\.env.local desde la plantilla
    copy .env.local.example .env.local > nul
)

echo Iniciando Next.js en http://localhost:3000 ...
pnpm dev