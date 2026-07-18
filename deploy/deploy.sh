#!/usr/bin/env bash
# Deploys one release of book_reservation on the Lightsail host.
#
# Streamed to the server by .github/workflows/deploy.yml with IMAGE,
# APP_VERSION, GHCR_USER and GHCR_TOKEN in the environment. Expects Docker
# (with the compose plugin) installed; docker-compose.yml and .env are
# rendered/copied to /opt/book_reservation/ by the workflow beforehand.
set -euo pipefail

: "${IMAGE:?IMAGE is required (e.g. ghcr.io/owner/repo:v1.2.3)}"
: "${APP_VERSION:?APP_VERSION is required (e.g. v1.2.3)}"

APP_DIR=/opt/book_reservation
cd "$APP_DIR"

for required in .env docker-compose.yml; do
    if [ ! -f "$required" ]; then
        echo "Missing $APP_DIR/$required — the deploy workflow should have copied it." >&2
        exit 1
    fi
done

mkdir -p data

# Pin the release in .env so compose interpolation (and any manual
# `docker compose up -d` on the server) keeps running exactly this version
# until the next deploy.
if grep -q '^IMAGE=' .env; then
    sed -i "s|^IMAGE=.*|IMAGE=$IMAGE|" .env
else
    printf '\nIMAGE=%s\n' "$IMAGE" >> .env
fi

if [ -n "${GHCR_TOKEN:-}" ]; then
    echo "$GHCR_TOKEN" | docker login ghcr.io -u "${GHCR_USER:-github-actions}" --password-stdin
fi

echo "==> Pulling $IMAGE"
docker compose pull web

# The image runs as a non-root user; the bind-mounted data dir must be
# writable by that uid or SQLite cannot create/open the database file.
echo "==> Ensuring data directory is writable by the container user"
APP_UID="$(docker run --rm "$IMAGE" id -u)"
sudo -n chown -R "$APP_UID" "$APP_DIR/data"

echo "==> Running database migrations"
docker compose run --rm web python manage.py migrate --noinput

echo "==> Starting new container"
docker compose up -d web

# Host port to probe; must match the compose port mapping.
HOST_PORT="$(sed -n 's/^HOST_PORT=//p' .env | tail -1)"
HOST_PORT="${HOST_PORT:-8000}"

echo "==> Waiting for health check"
for _ in $(seq 1 30); do
    if body=$(curl -fsS "http://127.0.0.1:$HOST_PORT/healthz" 2>/dev/null); then
        echo "healthz: $body"
        # JsonResponse renders with a space after the colon.
        if echo "$body" | grep -q "\"version\": \"${APP_VERSION#v}\""; then
            echo "==> Deploy of $APP_VERSION succeeded"
            docker image prune -f >/dev/null
            exit 0
        fi
        echo "Health endpoint is up but reports the wrong version." >&2
        break
    fi
    sleep 2
done

echo "==> Deploy failed — container did not become healthy" >&2
docker compose logs --tail 50 web >&2 || true
exit 1
