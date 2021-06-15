import os
from distutils.util import strtobool

from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key


def get_bool_from_env(name, default_value):
    if name in os.environ:
        value = os.getenv(name)
        try:
            return bool(strtobool(value))
        except ValueError as e:
            error_msg = "{} is an invalid value for {}".format(value, name)
            raise ImproperlyConfigured(error_msg) from e
    return default_value


def get_env_variable_or_default(name, default_value):
    if name in os.environ:
        return os.getenv(name)
    else:
        if type(default_value) == "int":
            return int(default_value)
        else:
            return default_value


def get_env_variable(var_name):
    try:
        return os.getenv(var_name)
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)


DEBUG = get_bool_from_env("DEBUG", True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generate_secret_key(filename):
    f = open(filename, "w")
    f.write(f"SECRET_KEY='{get_random_secret_key()}'")
    f.close()


try:
    from secret_key import SECRET_KEY
except ImportError:
    generate_secret_key(os.path.join(BASE_DIR, "secret_key.py"))
    from secret_key import SECRET_KEY  # noqa

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # main app
    "main_app",
    # rest framework
    "rest_framework",
    # rest framework token auth
    "rest_framework.authtoken",
    # swagger ui to view all available APIs
    "rest_framework_swagger",
    "drf_yasg",
    # indexing
    "haystack",
    "whoosh",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication"
    ]
}


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "storage_service.urls"

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

WSGI_APPLICATION = "storage_service.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": get_env_variable_or_default(
            "SQL_ENGINE", "django.db.backends.postgresql"
        ),
        "NAME": get_env_variable_or_default("SQL_DATABASE", "storage_service"),
        "USER": get_env_variable_or_default("SQL_USER", "postgres"),
        "PASSWORD": get_env_variable_or_default("SQL_PASSWORD", "password"),
        "HOST": get_env_variable_or_default("SQL_HOST", "localhost"),
        "PORT": get_env_variable_or_default("SQL_PORT", 5432),
    }
}

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack.backends.whoosh_backend.WhooshEngine",
        "PATH": os.path.join(os.path.dirname(__file__), "whoosh_index"),
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = "/static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "/media/"  # add this
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # add this
