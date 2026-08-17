# Imagen de producción para Render (u otro host Docker).
# El proyecto local usa Python 3.14; en producción se usa 3.13 (soporte amplio).
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=utf-8

WORKDIR /app

RUN pip install --no-cache-dir "poetry==2.1.1"

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

COPY . .

EXPOSE 8000

# Migraciones con reintentos (la BD tarda en estar lista) + gunicorn.
# Sustituye al preDeployCommand, que no está soportado en el plan free de Render.
CMD ["sh", "-c", "i=0; while [ $i -lt 12 ]; do python manage.py migrate --noinput && break; i=$((i+1)); echo 'migrate fallo, reintentando en 5s...'; sleep 5; done; exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60"]
