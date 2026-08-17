@echo off
REM ============================================================
REM  Pobla los datos ejecutando las tareas de scraping de forma
REM  sincronica (sin Celery ni Redis).
REM  - GitHub: repos en tendencia de hoy
REM  - Hacker News: historias de la portada
REM  - Product Hunt: launches de hoy (requiere PRODUCT_HUNT_TOKEN)
REM  - Metrica diaria agregada (MetricSnapshot)
REM ============================================================
setlocal
cd /d "%~dp0..\backend"

if not exist .env (
    echo [ERROR] No existe backend\.env
    exit /b 1
)

echo Ejecutando tareas de scraping ...
set PYTHONIOENCODING=utf-8
poetry run python manage.py shell -c "from github.tasks import fetch_github_trends; from hackernews.tasks import fetch_hackernews_stories; from producthunt.tasks import fetch_producthunt_launches; from analytics.tasks import aggregate_metrics; print('github:', fetch_github_trends()); print('hackernews:', fetch_hackernews_stories()); print('producthunt:', fetch_producthunt_launches()); print('metrics:', aggregate_metrics())"
echo.
echo Listo. El dashboard ya muestra los datos: http://localhost:3000