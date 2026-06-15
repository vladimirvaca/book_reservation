"""
Gunicorn config — tuned for a low-resource shared instance (512 MB RAM).

preload_app forks workers from an already-loaded Django process so the
interpreter and module cache are shared via Copy-on-Write, saving ~30 MB
per worker compared to loading each worker independently.

SQLite tolerates 2 sync workers fine at low traffic; bump to 4 only if the
instance is upgraded to 1 GB RAM.
"""
bind = "0.0.0.0:8000"
workers = 2
worker_class = "sync"
preload_app = True

timeout = 120
keepalive = 5

# Restart workers periodically to reclaim any memory leaks.
max_requests = 1000
max_requests_jitter = 100

# Log to stdout/stderr so Docker captures them.
accesslog = "-"
errorlog = "-"
loglevel = "warning"
