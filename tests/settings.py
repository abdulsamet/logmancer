from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Basic Django settings
SECRET_KEY = "devsecretkey"
DEBUG = True

# Applications
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "logmancer",
]

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Database - Use file-based SQLite for proper table creation
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Root URL configuration
ROOT_URLCONF = "tests.urls"

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Test optimizations
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Logmancer settings
LOGMANCER = {
    "ENABLE_MIDDLEWARE": True,
    "ENABLE_SIGNALS": True,
    "AUTO_LOG_EXCEPTIONS": True,
    "LOG_LEVEL": "INFO",
    "EXCLUDE_PATHS": [
        "/admin/jsi18n/",
        "/static/",
        "/media/",
    ],
    "EXCLUDE_MODELS": [
        "logmancer.LogEntry",
    ],
    "MASK_SENSITIVE_DATA": True,
    "SENSITIVE_FIELDS": [
        "password",
        "token",
        "secret",
        "key",
    ],
}

# For backward compatibility
LOGMANCER_AUTO_LOG_EXCEPTIONS = True
