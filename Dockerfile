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

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=book_reservation.settings

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
 && chown -R appuser:appgroup /app

USER appuser

# SQLite database and media uploads live outside the image; mount them as
# Docker volumes at runtime:
#   -v /host/data/db.sqlite3:/app/book_reservation/db.sqlite3
#   -v /host/data/media:/app/book_reservation/media_files
VOLUME ["/app/book_reservation/db.sqlite3", "/app/book_reservation/media_files"]

EXPOSE 8000

CMD ["gunicorn", "-c", "gunicorn.conf.py", "book_reservation.wsgi:application"]
