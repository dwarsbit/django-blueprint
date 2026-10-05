"""
Minimal Django settings for the blueprint test suite.

The package under test is a reusable app, so these settings contain only
what Django needs to boot the app registry and run migrations for the
media library: a secret key, contenttypes/auth (required by the app
registry machinery), SQLite in memory, and the blueprint apps themselves.
"""

import tempfile
from pathlib import Path

SECRET_KEY = "blueprint-test-suite"

DEBUG = False

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "blueprint",
    "blueprint.media_library",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# FileField storage: a throwaway directory so media tests never touch
# a real MEDIA_ROOT.
MEDIA_ROOT = Path(tempfile.mkdtemp(prefix="blueprint_test_media_"))
MEDIA_URL = "/media/"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
