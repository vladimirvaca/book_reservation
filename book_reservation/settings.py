import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Single source of truth for the release version; the release pipeline
# checks that git tags match this file.
APP_VERSION = (BASE_DIR.parent / 'VERSION').read_text(encoding='utf-8').strip()

# Short git SHA of the build, baked into the image by CI (docker build-arg).
# Empty when running from a checkout — which marks the build as "local".
APP_REVISION = os.environ.get('APP_REVISION', '').strip()[:7]

# Used to link the version shown in the UI to its release notes.
APP_SOURCE_URL = os.environ.get(
    'APP_SOURCE_URL', 'https://github.com/vladimirvaca/book_reservation'
).rstrip('/')

# ── Security ──────────────────────────────────────────────────────────────────
# Override DJANGO_SECRET_KEY in production via environment variable.
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    '@)*8xv5##1&@-72$f9a9$kg9-0#^1-p&4b(h2e$t5#g)piko6!'
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

# Whitespace-tolerant: "a.com, b.com" must not yield " b.com", which Django
# would silently never match (every request answers 400).
ALLOWED_HOSTS = [
    host.strip() for host in
    os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]

# Required when the site is served under a real domain (with or without TLS)
# so that POSTs pass Django's Origin check, e.g. "https://books.example.com".
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in
    os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]

# ── Application ───────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'login',
    'book',
    'reserve',
    'category',
]

# WhiteNoise must come directly after SecurityMiddleware.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # Below WhiteNoise so static files (already pre-compressed) skip it;
    # compresses dynamic HTML/JSON responses.
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'book_reservation.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'book_reservation.context_processors.release',
            ],
        },
    },
]

WSGI_APPLICATION = 'book_reservation.wsgi.application'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# ── Database ──────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # Overridable so Docker can keep the database on a mounted volume.
        'NAME': Path(os.environ.get('DJANGO_DB_PATH', BASE_DIR / 'db.sqlite3')),
        # Reuse connections across requests; reduces connection overhead.
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            # Wait up to 20 s before raising "database is locked" under
            # concurrent writes from multiple gunicorn workers.
            'timeout': 20,
            # WAL lets readers proceed while a write is in progress —
            # the main SQLite bottleneck with multiple gunicorn workers.
            # synchronous=NORMAL is safe with WAL and skips an fsync per
            # transaction.
            'init_command': (
                'PRAGMA journal_mode=WAL;'
                'PRAGMA synchronous=NORMAL;'
                'PRAGMA cache_size=-8000;'
            ),
            # Take the write lock at transaction start instead of upgrading
            # mid-transaction, avoiding spurious "database is locked" errors.
            'transaction_mode': 'IMMEDIATE',
        },
    }
}

# ── Password validation ───────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalisation ──────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = False

# ── Static files ──────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
# collectstatic writes here; WhiteNoise serves from here.
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Compress + fingerprint assets so browsers cache them indefinitely.
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
# The hashed manifest only exists after collectstatic, which test runs skip.
if 'test' in sys.argv:
    STORAGES['staticfiles']['BACKEND'] = (
        'django.contrib.staticfiles.storage.StaticFilesStorage'
    )

MEDIA_URL = '/media/'
# Overridable so Docker can keep uploads on a mounted volume.
MEDIA_ROOT = Path(os.environ.get('DJANGO_MEDIA_ROOT', BASE_DIR / 'media_files'))

# ── Logging ───────────────────────────────────────────────────────────────────
# Only emit warnings and above to keep log volume low on a shared instance.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
