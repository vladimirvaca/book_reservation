# ── Build stage ───────────────────────────────────────────────────────────────
# Separate stage to install deps and compile wheels without leaving build tools
# in the final image.
FROM python:3.13-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.13-slim

# CI overrides/extends these via docker/metadata-action; this static one
# covers local and manual builds.
LABEL org.opencontainers.image.description="Simple application to rent books, using Django and Jquery."

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=book_reservation.settings \
    DJANGO_DB_PATH=/data/db.sqlite3 \
    DJANGO_MEDIA_ROOT=/data/media

WORKDIR /app

# Copy installed packages from builder (keeps image lean — no compiler toolchain).
COPY --from=builder /install /usr/local

# Copy application code.
COPY . .

# Collect and compress static assets at build time so the running container
# does not need write access to the static directory.
RUN python manage.py collectstatic --noinput

# Create a non-root user and hand over ownership.
RUN addgroup --system appgroup \
 && adduser --system --ingroup appgroup --no-create-home appuser \
 && chown -R appuser:appgroup /app \
 && mkdir -p /data/media \
 && chown -R appuser:appgroup /data

USER appuser

# SQLite database (plus its WAL/SHM sidecar files) and media uploads live in
# /data; mount it as a volume at runtime:
#   -v /opt/book_reservation/data:/data
VOLUME ["/data"]

EXPOSE 8000

# 127.0.0.1 must therefore be present in DJANGO_ALLOWED_HOSTS.
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz')"

CMD ["gunicorn", "-c", "gunicorn.conf.py", "book_reservation.wsgi:application"]
