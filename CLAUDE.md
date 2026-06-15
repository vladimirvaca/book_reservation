# Book Reservation — Agent Guide

## Project overview

Django web application for library management. A librarian can manage book categories and books, then reserve them by time. Uses Django's auth system for access control — all views except login/index require authentication.

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

## Architecture

**Framework:** Django 5.2 LTS  
**Database:** SQLite (`book_reservation/db.sqlite3`)  
**Python:** 3.10+  

### Apps

| App | Purpose |
|-----|---------|
| `login` | Auth views (index, signin, dashboard) |
| `book` | Book CRUD (JSON API) |
| `category` | Category CRUD (JSON API) |
| `reserve` | Reservation logic (not yet implemented) |

### Request/response pattern

Views are **function-based** with `@login_required(login_url='/signin')`. Data mutation views return `JsonResponse` for AJAX consumption; page views return `render()`.

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

### URL patterns

All URL configs use `re_path()` with regex patterns (Django 5.x style):

```python
from django.urls import re_path
urlpatterns = [
    re_path(r'^$', views.category, name='category'),
    re_path(r'^edit/(?P<category_id>\d+)', views.edit_category, name='category_edit'),
]
```

### Models

`Book` belongs to `Category` via ForeignKey with `on_delete=models.CASCADE`. Both use `__str__` (Python 3).

```python
class Book(models.Model):
    number_serie = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    category_book = models.ForeignKey(Category, on_delete=models.CASCADE)
    resume = models.CharField(max_length=100)

    def __str__(self):
        return self.name
```

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
`base_templates/base_template.html` is the base layout with Bootstrap 4, jQuery 3, and DataTables. All pages extend it via `{% extends %}`.

### Settings

`settings.py` lives in `book_reservation/` (same package as `urls.py`, `wsgi.py`).  
`BASE_DIR` uses `pathlib.Path` and points to the `book_reservation/` config directory.  
`STATICFILES_DIRS` points to `book_reservation/static/`.  
`MEDIA_ROOT` points to `book_reservation/media_files/`.

## Known issues / tech debt

- `edit_book` and `edit_category` views use `id` (builtin) instead of `book_id` / `category_id` parameter — bug inherited from original code.
- `get_categories_search` builds SQL with string formatting — SQL injection risk. Should be migrated to ORM.
- Raw SQL in `get_books` and `get_categories` can be replaced with `Book.objects.all()` / `Category.objects.all()`.
- `reserve` app has no models or views implemented yet.
