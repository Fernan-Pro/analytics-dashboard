# Analytics Dashboard

Dashboard de analytics que consume las APIs públicas de **GitHub**, **Hacker News** y **Product Hunt**,
los almacena en **PostgreSQL** y los expone mediante **Django REST Framework** + un frontend
**Next.js** con gráficos Recharts y tablas TanStack Table.

## Arquitectura

```
                          +-----------------+
                          |   Celery Beat    |  (schedule cada 15-60 min)
                          +--------+--------+
                                   | envia tareas
                                   v
+------------------+        +---------------+        +-------------------+
|  GitHub API      |        |   Celery      |        |   Redis (broker)  |
|  Hacker News     |------->|   worker      |<-------|                   |
|  Product Hunt    | fetch  +-------+-------+        +-------------------+
+------------------+                | guarda
                                    v
                            +---------------+
                            |  PostgreSQL   |  Django 5 + DRF
                            +-------+-------+
                                    ^
                          /api/github/trends/
                          /api/hackernews/stories/
              +------------------+-------------------+
              | Next.js 16       |  Recharts (graficos)  |
              | (App Router)     |  TanStack Table       |
              | TanStack Query   |  Tailwind v4          |
              +------------------+-----------------------+
```

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3.14, Django 5.2, DRF 3.18, django-filter, Celery 5.6, psycopg 3 |
| Base de datos | PostgreSQL 18 (local) o PostgreSQL 16 (Docker) |
| Cache / broker | Redis 7 (vía Docker o Memurai en Windows) |
| Frontend | Next.js 16, React 19, Tailwind v4, Recharts, TanStack Query + Table |
| Paquetes | Poetry 2 (backend), pnpm 11 (frontend) |

## Estructura

```
analytics-dashboard/
├── backend/
│   ├── config/          # settings, urls, celery
│   ├── apps/
│   │   ├── github/      # modelo GitHubTrend + servicio + tarea
│   │   ├── hackernews/  # modelo HackerNewsStory + servicio + tarea (API Algolia)
│   │   ├── producthunt/ # modelo ProductHuntLaunch + servicio + tarea
│   │   └── analytics/   # MetricSnapshot, agregacion, summary, export CSV
│   ├── .env             # variables (gitignored)
│   └── manage.py
├── frontend/
│   ├── src/app/         # dashboard (page.tsx)
│   ├── src/components/  # ui/, charts/, tables/, providers/
│   ├── src/lib/         # api client, utils, helpers de metricas
│   ├── src/types/       # tipos TS de la API
│   └── vendor/          # tarballs de next/swc (ver Troubleshooting)
├── scripts/             # scripts de arranque y datos (Windows)
├── docker-compose.yml   # PostgreSQL + Redis
└── .env.example
```

## Requisitos

- Python 3.12+ y [Poetry](https://python-poetry.org/)
- Node 20+ y [pnpm](https://pnpm.io/)
- PostgreSQL en ejecución (local o `docker compose up -d postgres`)
- Redis (solo para Celery; opcional si usas `scripts\fetch-data.cmd`)

## Puesta en marcha

### 1. Base de datos

```bash
# Con PostgreSQL local: crea la BD y el usuario
# (ajusta nombres/contraseñas a tu entorno)
psql -U postgres -c "CREATE USER analytics_user WITH PASSWORD 'tu_password';"
psql -U postgres -c "CREATE DATABASE analytics OWNER analytics_user;"
```

O con Docker:

```bash
docker compose up -d postgres
```

### 2. Backend

```bash
cd backend
copy .env.example .env        # completa los valores
poetry install
poetry run python manage.py migrate
poetry run python manage.py runserver 127.0.0.1:8000
```

### 3. Frontend

```bash
cd frontend
copy .env.local.example .env.local
pnpm install
pnpm dev                      # http://localhost:3000
```

O simplemente:

```cmd
scripts\start-all.cmd         # backend + frontend en ventanas separadas
```

### 4. Poblar datos

```cmd
scripts\fetch-data.cmd        # ejecuta el scraping una vez, sin Celery
```

O con Celery (requiere Redis):

```cmd
scripts\start-celery.cmd      # verifica Redis y lanza worker + beat
```

## Variables de entorno

| Variable | Dónde | Descripción |
|---|---|---|
| `DJANGO_SECRET_KEY` | `backend/.env` | Clave secreta de Django |
| `POSTGRES_*` | `backend/.env` | Conexión a PostgreSQL |
| `REDIS_HOST/PORT`, `CELERY_BROKER_URL` | `backend/.env` | Broker de Celery |
| `CORS_ALLOWED_ORIGINS` | `backend/.env` | Orígenes permitidos (ej. `http://localhost:3000`) |
| `GITHUB_TOKEN` | `backend/.env` | Opcional. Mejora el rate limit de la GitHub Search API |
| `PRODUCT_HUNT_TOKEN` | `backend/.env` | Necesario para Product Hunt (Dev Token en https://www.producthunt.com/v2/oauth/applications) |
| `NEXT_PUBLIC_API_URL` | `frontend/.env.local` | URL base de la API (default `http://localhost:8000/api`) |

> **Nota sobre Reddit:** Reddit eliminó el acceso self-service a su API (Responsible Builder
> Policy, nov. 2025) y bloquea los endpoints `.json` sin autenticación (mayo 2026). La fuente
> de comunidad del proyecto es **Hacker News**, cuya API oficial (Algolia) es gratuita y sin
> credenciales.

## Endpoints

| Endpoint | Filtros | Descripción |
|---|---|---|
| `GET /api/github/trends/` | `language`, `start_date`, `end_date`, `min_stars`, `ordering`, `page_size` | Repos en tendencia |
| `GET /api/hackernews/stories/` | `author`, `min_points`, `min_comments`, `start_date`, `end_date` | Historias de Hacker News |
| `GET /api/producthunt/launches/` | `start_date`, `end_date`, `min_votes` | Launches de Product Hunt |
| `GET /api/metrics/snapshot/` | `start_date`, `end_date` | `summary` (KPIs agregados) + `history` (serie diaria) |
| `GET /api/export/csv/?category=` | los mismos filtros de cada fuente | Export CSV (streaming, `Content-Disposition: attachment`) |

Ejemplos:

```bash
# Repos Python de la ultima semana ordenados por estrellas
curl "http://localhost:8000/api/github/trends/?language=Python&start_date=2026-08-08&ordering=-stars"

# Historias de Hacker News con mas de 100 puntos
curl "http://localhost:8000/api/hackernews/stories/?min_points=100"

# KPIs agregados
curl "http://localhost:8000/api/metrics/snapshot/"

# Export CSV de Hacker News con filtro de puntos
curl -OJ "http://localhost:8000/api/export/csv/?category=hackernews&min_points=100"
```

Paginación: `page_size` (default 25, máx 100). Respuesta estándar `{count, next, previous, results}`.

## Celery

- `config/celery.py` define la app; el schedule está en `settings.py` (`CELERY_BEAT_SCHEDULE`):

| Tarea | Cada |
|---|---|
| `github.tasks.fetch_github_trends` | 30 min |
| `hackernews.tasks.fetch_hackernews_stories` | 15 min |
| `producthunt.tasks.fetch_producthunt_launches` | 60 min |
| `analytics.tasks.aggregate_metrics` | diario 00:05 UTC |

- Todas las tareas son idempotentes (upsert por URL) y las consultas externas usan retry
  con backoff y respeto de rate limits (`X-RateLimit-Reset`, `Retry-After`).

## Troubleshooting

| Problema | Solución |
|---|---|
| Hacker News devuelve 403 / no resuelve DNS | Algolia y Google están bloqueados en algunas redes (ISP/país). El código funciona en cualquier red normal y en los servicios cloud (Render, Vercel); localmente usa VPN o la API en otro entorno |
| Product Hunt sin datos | Falta `PRODUCT_HUNT_TOKEN` |
| Celery no arranca | Redis no está corriendo. `docker compose up -d redis` o usa `scripts\fetch-data.cmd` |
| `UnicodeEncodeError` en consola (cp1252) | Ejecuta con `set PYTHONIOENCODING=utf-8` (los scripts ya lo hacen) |
| `pnpm install` lento o timeouts | `pnpm-workspace.yaml` ya configura timeouts largos (`fetchTimeout: 600000`, `fetchRetries: 15`) |
| typescript-eslint 8.67.0 roto | Pinneado a 8.66.0 vía `pnpm.overrides` en `pnpm-workspace.yaml` |
| `@tanstack/react-table` v9 | v9 es un rewrite incompatible con la API clásica; el proyecto usa la v8 estable (8.21.x) |
| CSV con caracteres raros al abrirlo | El archivo es UTF-8 (`charset=utf-8` en el header). Excel: Datos > Obtener datos > Desde archivo CSV y elegir UTF-8 |

## Producción (deploy gratuito)

| Servicio | URL | Notas |
|---|---|---|
| Frontend (Vercel) | https://analytics-dashboard-eta-peach.vercel.app | Import del repo con Root Directory `frontend` y `NEXT_PUBLIC_API_URL` |
| Backend (Render) | https://analytics-dashboard-api-u27v.onrender.com | Blueprint `render.yaml` (Docker + Postgres free) |
| Repositorio | https://github.com/Fernan-Pro/analytics-dashboard | Público, branch `master` |

- **Cron de datos**: `.github/workflows/fetch-data.yml` llama cada 15 min a
  `POST /api/admin/fetch/` (header `X-Admin-Token`, secret de GitHub `ADMIN_FETCH_TOKEN`).
  Sustituye a Celery en producción y mantiene el servicio de Render activo (free tier).
- **Migraciones**: se ejecutan en el arranque del contenedor (el plan free de Render no
  soporta `preDeployCommand`).
- **Nota free tier**: la base de datos gratuita de Render expira a los 30 días
  (hay que re-crearla o migrar); el servicio entra en suspensión tras 15 min de
  inactividad (el cron lo despierta cada 15 min).
- **Endpoints en producción** (mismos paths que local):
  `https://analytics-dashboard-api-u27v.onrender.com/api/metrics/snapshot/`, `/api/github/trends/`,
  `/api/hackernews/stories/`, `/api/producthunt/launches/`, `/api/export/csv/?category=...`.