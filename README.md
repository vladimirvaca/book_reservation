# Book Reservation

A Django web application for library management. Patrons can reserve books without an account; librarians manage the full catalog and track reservation lifecycle from a protected dashboard.

## Features

**Public (no login required)**
- Reserve a book by entering a DNI/identifier, full name, start date, and return date
- Browse available books from the landing page

**Admin dashboard (login required)**
- Manage book categories — create, edit, delete, live search
- Manage books — create, edit, delete, assign to categories
- View all reservations in a live DataTable
- Track reservation status: **Reserved → Checked Out → Returned** (overdue computed automatically when the return date passes)
- Check out and return books with one click; clear reservations

## Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2 LTS |
| WSGI server | Gunicorn 23 |
| Static files | WhiteNoise 6 (compressed + fingerprinted) |
| Database | SQLite |
| Python | 3.13 |
| Frontend | Bootstrap 4, jQuery 3.7.1, DataTables 1.10.19, FontAwesome 5 |

## Local development

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux / macOS

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply migrations
python manage.py migrate

# 4. Create an admin user
python manage.py createsuperuser

# 5. Start the dev server
python manage.py runserver
```

Open http://127.0.0.1:8000 — the landing page is public. Sign in at `/signin/` to access the dashboard.

## Docker deployment

### Build the image

```bash
docker build -t book-reservation .
```

Static assets are collected and compressed at build time; no extra step needed.

### Run

```bash
docker run -d \
  -p 8000:8000 \
  -e DJANGO_SECRET_KEY='your-production-secret-key' \
  -e DJANGO_DEBUG='False' \
  -e DJANGO_ALLOWED_HOSTS='yourdomain.com,127.0.0.1' \
  -v /host/data:/data \
  book-reservation
```

The `/data` bind-mount persists the SQLite database (including its WAL sidecar files) and uploaded media across container restarts and redeployments. Keep `127.0.0.1` in `DJANGO_ALLOWED_HOSTS` so the built-in container health check (`/healthz`) passes.

### First run — create the database and admin user

```bash
# Apply migrations (only needed once, or after model changes)
docker run --rm \
  -e DJANGO_SECRET_KEY='your-production-secret-key' \
  -v /host/data:/data \
  book-reservation \
  python manage.py migrate

# Create the admin account
docker run --rm -it \
  -e DJANGO_SECRET_KEY='your-production-secret-key' \
  -v /host/data:/data \
  book-reservation \
  python manage.py createsuperuser
```

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | dev key (insecure) | **Required in production.** Django secret key. |
| `DJANGO_DEBUG` | `True` | Set to `False` in production. |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated list of allowed hostnames. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | *(empty)* | Comma-separated origins incl. scheme, e.g. `https://books.example.com`. Needed when serving under a domain. |
| `DJANGO_DB_PATH` | `book_reservation/db.sqlite3` | SQLite file location (the Docker image sets `/data/db.sqlite3`). |
| `DJANGO_MEDIA_ROOT` | `book_reservation/media_files` | Media upload directory (the Docker image sets `/data/media`). |

> **Note:** A reverse proxy (nginx, Caddy, Traefik) in front of the container is recommended for TLS termination and domain routing when sharing a Lightsail instance with other apps.

## CI / CD

GitHub Actions runs three jobs on every push and pull request to `master`:

| Job | What it does |
|---|---|
| **Lint** | `pylint --errors-only` across all apps · `isort --check` for import ordering |
| **Test** | `python manage.py test` |
| **Docker** | Builds the image and pushes to `ghcr.io` (master pushes only, after lint + test pass) |

The Docker job uses GitHub Actions layer cache to speed up rebuilds and tags each image with both `latest` and the commit SHA for traceability.

### Releases & automatic deployment

Pushing a `vX.Y.Z` tag triggers the **Release** pipeline: version check against the `VERSION` file, full test run, versioned image push to GHCR, GitHub Release with a source artifact, and an automatic SSH deploy to the AWS Lightsail instance, where Docker Compose pulls and runs the newly released image. The running version is exposed at `GET /healthz`. See [RELEASING.md](RELEASING.md) for the full release/rollback procedure and one-time server setup.

## Project structure

```
book_reservation/
├── book/               # Book CRUD (models, views, forms, URLs)
├── category/           # Category CRUD + live search
├── login/              # Auth views: index, sign-in, dashboard
├── reserve/            # Public reservation + dashboard management
└── book_reservation/   # Django config — settings, root URLs, templates, static
    ├── static/
    │   ├── css/        # main.css, dashboard-style.css, index-style.css, login-style.css
    │   └── js/         # book.js, category.js, reserve.js, reservations.js, utilities.js
    └── templates/
        ├── base_templates/base_template.html
        ├── forms/      # Reusable modal partials
        ├── book.html, category.html, dashboard.html, index.html, login.html
```

### Apps

| App | Purpose |
|---|---|
| `login` | Landing page, sign-in, protected dashboard home with reservation table |
| `book` | Add, edit, delete, and list books |
| `category` | Add, edit, delete, search, and list categories |
| `reserve` | Public reservation form · dashboard management (status updates, delete) |

## Architecture

- Views are **function-based** (`@login_required(login_url='/signin')` on protected views; no decorator on public endpoints).
- Data endpoints return `JsonResponse` consumed via jQuery AJAX. Page views return `render()`.
- URL configs use `re_path()` with regex patterns throughout.
- All templates extend `base_templates/base_template.html`, which loads Bootstrap 4, jQuery 3.7.1, DataTables, FontAwesome 5, and shared CSS/JS.
- The dashboard uses DataTables with server-side AJAX reload — no full page refresh on CRUD operations.
- Reservation status (`reserved` / `checked_out` / `returned`) is stored in the database; `overdue` is derived at query time when `end_date < today` and status is not `returned`.

## License

MIT — free to use, modify, and contribute.
