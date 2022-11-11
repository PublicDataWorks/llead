"""
Django settings for ipno project.

Generated by 'django-admin startproject' using Django 3.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import environ
import os
from datetime import timedelta

import structlog
from google.cloud.logging.handlers import StructuredLogHandler
from google.cloud.logging_v2.handlers import setup_logging

from utils.log_utils import drop_health_check_event

# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = environ.Path(__file__) - 4
APPS_DIR = BASE_DIR.path('ipno')

env = environ.Env()

env_file = f'{BASE_DIR}/.env'

if os.path.isfile(env_file):
    environ.Env.read_env(env_file)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = env.str('DJANGO_SECRET_KEY', None)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEST = False

ALLOWED_HOSTS = ['*']

# Application definition

DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_elasticsearch_dsl',
    'martor',
    'django_rest_passwordreset',
    'anymail',
    'adminsortable',
    'adminsortable2',
    'mapbox_location_field',
)

LOCAL_APPS = (
    'authentication',
    'app_config',
    'core',
    'q_and_a',
    'documents',
    'departments',
    'officers',
    'complaints',
    'use_of_forces',
    'analytics',
    'data',
    'news_articles',
    'tasks',
    'people',
    'appeals',
    'feedbacks',
    'historical_data',
)

AUTH_USER_MODEL = 'authentication.User'

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_structlog.middlewares.RequestMiddleware',
]

CACHES = {
   'default': {
      'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
      'LOCATION': 'ipno_cache_table',
   }
}

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [os.path.join(APPS_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str('POSTGRES_DB', 'ipno'),
        'USER': env.str('POSTGRES_USER', 'ipno'),
        'PASSWORD': env.str('POSTGRES_PASSWORD', 'ipno'),
        'HOST': env.str('POSTGRES_HOST', 'db'),
        'PORT': 5432,
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = str(APPS_DIR('static'))

# Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
}

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': env.str('ELASTICSEARCH_HOST', 'elasticsearch:9200'),
    },
}

WRGL_API_KEY = env.str('WRGL_API_KEY', None)

DROPBOX_APP_KEY = env.str('DROPBOX_APP_KEY', None)
DROPBOX_APP_SECRET = env.str('DROPBOX_APP_SECRET', None)
DROPBOX_REFRESH_TOKEN = env.str('DROPBOX_REFRESH_TOKEN', '')

MAPBOX_KEY = env.str('MAPBOX_KEY', None)

FROM_EMAIL = os.getenv('FROM_EMAIL')
FEEDBACK_FROM_EMAIL = os.getenv('FEEDBACK_FROM_EMAIL')
FEEDBACK_TO_EMAIL = os.getenv('FEEDBACK_TO_EMAIL')

SENDINBLUE_API_URL = "https://api.sendinblue.com/v3/"

WRGL_USER = os.getenv('WRGL_USER', '')
NEWS_ARTICLE_WRGL_REPO = 'news_article'
NEWS_ARTICLE_OFFICER_WRGL_REPO = 'news_article_officer'

SIMPLE_LOG = env.bool('SIMPLE_LOG', False)

timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")
shared_processors = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.filter_by_level,
    structlog.processors.format_exc_info,
    timestamper,
    drop_health_check_event,
    structlog.processors.UnicodeDecoder(),
    structlog.processors.StackInfoRenderer(),
    structlog.stdlib.PositionalArgumentsFormatter(),
]

structlog.configure(
    processors=shared_processors + [
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

if not SIMPLE_LOG:
    handler = StructuredLogHandler()
    setup_logging(handler)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
}
