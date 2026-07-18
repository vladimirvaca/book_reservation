# Releasing & Deployment

## Versioning

The project follows [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`).
The single source of truth is the `VERSION` file at the repo root; the app
exposes it at runtime via `GET /healthz`:

```json
{"status": "ok", "version": "1.0.0"}
```

The release pipeline refuses to run if the pushed tag does not match `VERSION`.

## Cutting a release

```bash
# 1. Bump the version (e.g. 1.1.0), commit to master
echo 1.1.0 > VERSION
git add VERSION
git commit -m "Bump version to 1.1.0"
git push

# 2. Tag and push the tag — this triggers the release pipeline
git tag v1.1.0
git push origin v1.1.0
```

The `Release` workflow (`.github/workflows/release.yml`) then runs:

1. **verify** — checks tag == `VERSION`, runs the full test suite.
2. **docker** — builds and pushes `ghcr.io/<owner>/<repo>:v1.1.0` and `:latest`.
3. **github-release** — creates a GitHub Release with auto-generated notes
   and a source tarball artifact.
4. **deploy** — SSHes into the Lightsail instance and ships the new image
   (see below).

To redeploy or roll back, run the **Deploy** workflow manually from the
Actions tab and enter any previously released tag (e.g. `v1.0.0`).

## One-time Lightsail setup

On a fresh Ubuntu Lightsail instance:

```bash
# Install Docker (includes the compose plugin used by the deploy)
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER   # log out & back in afterwards

# App directory (the deploy workflow copies docker-compose.yml and .env here)
sudo mkdir -p /opt/book_reservation/data
sudo chown -R $USER /opt/book_reservation
```

That's all — no config files are created by hand on the instance. The
production `.env` is rendered from GitHub secrets/variables on every deploy.

Open the app port (default 8000, or 80/443 if you front it with a reverse
proxy) in the Lightsail firewall ("Networking" tab).

### GitHub repository secrets

| Secret | Value |
|--------|-------|
| `LIGHTSAIL_HOST` | Public IP / hostname of the instance |
| `LIGHTSAIL_USER` | SSH user, e.g. `ubuntu` |
| `LIGHTSAIL_SSH_KEY` | Contents of the private key (PEM) for that user |
| `DJANGO_SECRET_KEY` | Production secret key — generate with `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `LIGHTSAIL_PORT` | *(optional)* SSH port if not 22 |

### GitHub repository variables

Settings → Secrets and variables → Actions → **Variables** (non-sensitive
config; readable in logs, unlike secrets):

| Variable | Value |
|----------|-------|
| `DJANGO_ALLOWED_HOSTS` | Public domain / IP, e.g. `books.example.com` (`127.0.0.1` and `localhost` are appended automatically for health checks) |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | *(optional)* Origins incl. scheme, e.g. `https://books.example.com` |
| `HOST_PORT` | *(optional)* Host port compose publishes; defaults to 8000 |

No registry credential is needed on the server: the workflow logs Docker in
with the run's `GITHUB_TOKEN` (read-only `packages` scope).

Recommended: create a **production** environment in repo Settings →
Environments; the deploy job targets it, so you get a deployment history and
can add required reviewers as a manual approval gate.

## What a deploy does on the server

The server runs the app via Docker Compose. Layout on the instance:

```
/opt/book_reservation/
├── docker-compose.yml   # copied from deploy/ by the workflow on every deploy
├── .env                 # rendered from GitHub secrets/vars on every deploy;
│                        # deploy.sh then pins IMAGE=<released tag> in it
└── data/                # SQLite database + media uploads (compose volume)
```

The workflow first renders `.env` (from `DJANGO_SECRET_KEY`,
`DJANGO_ALLOWED_HOSTS`, …) and copies it to the server together with
`docker-compose.yml`. Then `deploy/deploy.sh` (streamed over SSH, never
stored on the server):

1. Pins `IMAGE=ghcr.io/<owner>/<repo>:vX.Y.Z` in `/opt/book_reservation/.env`
   so compose always resolves to the exact released version.
2. `docker compose pull web` — fetches the new image from GHCR.
3. `docker compose run --rm web python manage.py migrate --noinput`.
4. `docker compose up -d web` — recreates the container on the new image.
5. Polls `http://127.0.0.1:<HOST_PORT>/healthz` until it responds **and
   reports the deployed version** — the deploy fails (with container logs in
   the Actions output) if it doesn't come up within ~60 s.
6. Prunes dangling images from previous releases.

Because the version is pinned in `.env`, manual operations on the server are
safe and ordinary compose commands:

```bash
cd /opt/book_reservation
docker compose logs -f web      # tail application logs
docker compose restart web      # restart current version
docker compose up -d web        # recreate (still the pinned version)
```
