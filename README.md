# Book Reservation

A web application for library management. Librarians can manage book categories and books, then reserve them by time. Built with Django and a Bootstrap 4 frontend.

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.2 LTS |
| Database | SQLite |
| Python | 3.10+ |
| Frontend | Bootstrap 4, jQuery 3.7.1, DataTables 1.10.19 |
| Icons | FontAwesome 5 |

## Getting started

```bash
# 1. Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py migrate

# 4. Create an admin user
python manage.py createsuperuser

# 5. Start the development server
python manage.py runserver
```

Then open http://127.0.0.1:8000 in your browser.

## Project structure

```
book_reservation/
├── book/               # Book CRUD
├── category/           # Category CRUD
├── login/              # Authentication (sign in, dashboard)
├── reserve/            # Reservation logic (in progress)
└── book_reservation/   # Django config (settings, root URLs, templates, static)
```

### Apps

| App | Purpose |
|-----|---------|
| `login` | Index page, sign-in, dashboard |
| `book` | Add, edit, delete, and list books |
| `category` | Add, edit, delete, and search categories |
| `reserve` | Time-based book reservations *(not yet implemented)* |

## Architecture notes

- Views are **function-based** and protected with `@login_required`.
- Data endpoints return `JsonResponse` consumed via jQuery AJAX; page views return `render()`.
- URL configs use `re_path()` with regex patterns.
- Templates extend `base_templates/base_template.html`, which loads all shared CSS/JS.

## Known issues

- `get_categories_search` builds a SQL `LIKE` query with string formatting — SQL injection risk. Should be migrated to the ORM (`Category.objects.filter(category__icontains=...)`).
- `get_books` and `get_categories` use raw SQL (`objects.raw(...)`) where `objects.all()` / `values()` would suffice.
- The `reserve` app has no models or views implemented yet.

## License

MIT — feel free to use, modify, and contribute. Any improvement or contribution is welcome.
