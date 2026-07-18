# Book Reservation — Agent Guide

## Project overview

Django web application for library management. Patrons reserve books from the public landing page (no account needed); librarians manage categories, books, reservations, and admin users from a login-protected dashboard. Uses Django's auth system for access control — all views except the landing page, sign-in, and the public reservation endpoints require authentication.

## Running the project

```bash
# Create and activate venv
python -m venv .venv
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # Linux/macOS

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Run the test suite with `python manage.py test` (80 tests across all apps). CI lints with `pylint --rcfile=.pylintrc --errors-only` and `isort --check-only`.

## Architecture

**Framework:** Django 5.2 LTS  
**Database:** SQLite (WAL mode, path overridable via `DJANGO_DB_PATH`)  
**Python:** 3.13 (CI); 3.10+ works  

### Apps

| App | Purpose |
|-----|---------|
| `login` | Auth views (index, signin, dashboard) + admin-user CRUD |
| `book` | Book CRUD (JSON API) |
| `category` | Category CRUD + live search (JSON API) |
| `reserve` | Public reservation form + dashboard reservation management (status lifecycle: reserved → checked_out → returned; overdue derived at query time) |

### Request/response pattern

Views are **function-based**; protected ones use `@login_required(login_url='/signin')` (public reservation endpoints have no decorator). Data mutation views return `JsonResponse` for AJAX consumption; page views return `render()`.

```python
@login_required(login_url='/signin')
def save_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "1", "type": "success", "message": "..."})
        return JsonResponse({"status": "-1", "type": "error", "message": "Form not valid."})
    return None
```

All list/search endpoints use the ORM (`values()`, `select_related`) — no raw SQL anywhere.

### URL patterns

All URL configs use `re_path()` with regex patterns (Django 5.x style):

```python
from django.urls import re_path
urlpatterns = [
    re_path(r'^$', views.category, name='category'),
    re_path(r'^edit/(?P<category_id>\d+)', views.edit_category, name='category_edit'),
]
```

The root URLconf (`book_reservation/urls.py`) also defines `GET /healthz` — an anonymous probe returning `{"status": "ok", "version": <APP_VERSION>}`, used by the Docker HEALTHCHECK and for verifying a rollout landed.

### Models

`Book` belongs to `Category` (FK, CASCADE). `Reservation` belongs to `Book` (FK, CASCADE) with a `status` choice field (`reserved` / `checked_out` / `returned`). All models use `__str__`.

### Forms

ModelForm subclasses with explicit field declarations:

```python
class BookForm(forms.ModelForm):
    number_serie = forms.CharField(required=True)
    class Meta:
        model = Book
        fields = ['number_serie', 'name', 'category_book', 'resume']
```

### Templates

`book_reservation/templates/` is the template root (configured in `settings.py`).  
`base_templates/base_template.html` is the base layout with Bootstrap 4, jQuery 3, and DataTables. All pages extend it via `{% extends %}`. Reusable modal partials live in `templates/forms/`.

### Settings

`settings.py` lives in `book_reservation/` (same package as `urls.py`, `wsgi.py`); `BASE_DIR` points there.  
`APP_VERSION` is read from the root `VERSION` file — the single source of truth for releases.  
Env-configurable: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `DJANGO_DB_PATH`, `DJANGO_MEDIA_ROOT`.  
SQLite runs with `journal_mode=WAL`, `synchronous=NORMAL`, and `transaction_mode=IMMEDIATE`. Static files: WhiteNoise (compressed + manifest; plain storage under `manage.py test`). `GZipMiddleware` compresses dynamic responses.

### Tests

Each app has a `tests.py`; shared helpers in root-level `testutils.py` (`LoginRequiredTestsMixin` verifies protected URLs redirect anonymous users to `/signin`).

## CI/CD & releases

Two workflows in `.github/workflows/`:

- **ci.yml** — push/PR to master: pylint (errors only), isort, tests; on master push also builds/pushes the Docker image to GHCR (`:latest` + commit SHA).
- **release.yml** — on `vX.Y.Z` tag: verifies tag matches `VERSION`, then lint (pylint errors-only + isort) and tests gate everything; pushes `ghcr.io/<repo>:vX.Y.Z` + `:latest` with OCI labels (version/revision/source, via docker/metadata-action — containers inherit them, used with Traefik), and creates a GitHub Release whose notes list the commits since the previous tag. The pipeline ends there — **no automated deployment**; released images are pulled and run manually on the target host (procedure in `RELEASING.md`).

To cut a release: bump `VERSION`, commit, tag `vX.Y.Z`, push the tag.

The Docker image stores SQLite + media under a single `/data` volume (single-file mounts would break WAL sidecar files).
