# Releasing

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

1. **verify** — checks tag == `VERSION`, then runs pylint, isort, and the
   full test suite. **Nothing is published unless all of them pass.**
2. **docker** — builds and pushes `ghcr.io/<owner>/<repo>:v1.1.0` and
   `:latest`. The image carries standard OCI labels
   (`org.opencontainers.image.version`, `.revision`, `.source`,
   `.created`, …) that containers inherit at runtime, so label-driven
   tooling such as Traefik can identify what is running.
3. **github-release** — creates a GitHub Release containing the list of
   commits since the previous tag, the image reference, and a source
   tarball artifact.

That's the end of the pipeline: every release yields a GitHub Release plus a
versioned, immutable, labeled Docker image on GHCR. Deployment is a
separate, manual concern.

## Deploying a released image

Pull the versioned image on any Docker host and run it (see the README's
"Docker deployment" section for the full run/migrate commands and
environment variables):

```bash
docker pull ghcr.io/<owner>/<repo>:v1.1.0
```

> **GHCR visibility:** images are private by default. Either make the
> package public (GitHub → Packages → package settings → Change visibility)
> or log the host in with a personal access token that has `read:packages`:
> `echo $PAT | docker login ghcr.io -u <username> --password-stdin`

If the host runs the app via Docker Compose with the image tag kept in an
`.env` file (`IMAGE=ghcr.io/<owner>/<repo>:v1.1.0`), updating to a new
release is:

```bash
cd /path/to/app
sed -i 's|^IMAGE=.*|IMAGE=ghcr.io/<owner>/<repo>:v1.1.0|' .env
docker compose pull web
docker compose run --rm -T web python manage.py migrate --noinput
docker compose up -d --force-recreate web
curl http://127.0.0.1:8000/healthz   # should report the new version
```

## Running behind Traefik

The image ships with OCI identification labels baked in (version, git
revision, source repo), and containers inherit them — inspect with
`docker inspect <container> --format '{{json .Config.Labels}}'`.

Traefik *routing* rules are deployment-specific, so they belong in the
host's compose file rather than the image:

```yaml
services:
  web:
    image: "${IMAGE}"
    labels:
      - traefik.enable=true
      - traefik.http.routers.books.rule=Host(`books.example.com`)
      - traefik.http.routers.books.entrypoints=websecure
      - traefik.http.routers.books.tls.certresolver=letsencrypt
      - traefik.http.services.books.loadbalancer.server.port=8000
```

With Traefik terminating TLS, set `DJANGO_CSRF_TRUSTED_ORIGINS`
(e.g. `https://books.example.com`) in the app's environment.
