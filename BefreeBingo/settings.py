"""
Django settings for BefreeBingo project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6vjfmub=lt809o-jomgcv+)e6ace7wh%x&!awez9zup*p)fo=p'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Deps
    'rest_framework',
    'corsheaders',
    'djmoney',
    'rest_framework_swagger',
    'drf_yasg',
    'widget_tweaks',

    # Apps
    'user',
    'bets',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'BefreeBingo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'BefreeBingo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'templates', 'assets'),
)

AUTH_USER_MODEL = 'user.User'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 2,
    'DEFAULT_PERMISSION_CLASSES': (
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'user.authentication.TokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ),
    # 'DEFAULT_FILTER_BACKENDS': (
    #     'django_filters.rest_framework.DjangoFilterBackend',
    # ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    # 'EXCEPTION_HANDLER': 'core.common.handlers.custom_exception_handler',
    'DATETIME_FORMAT': '%d.%m.%y %H:%M',
    'DATE_FORMAT': '%d.%m.%y',
    'DATE_INPUT_FORMATS': [
        '%d.%m.%y'
    ],
    'TIME_FORMAT': '%H:%M',
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}

# CORS_ORIGIN_WHITELIST = ['http://localhost:3000']

CORS_ORIGIN_ALLOW_ALL = True


PIASTRIX_CONFIG = {
    'SHOP_SECRET': 'rpqo43hP6YWZVHLp',
    'SHOP_ID': 3799,
    'BASE_URL': 'https://core.piastrix.com/invoice/create'
}

BITCHANGE_CONFIG = {
    'SHOP_ID': 'BlqWarhVLHmqA8DdPoZNK00xebYNDf',
    'SHOP_SECRET': 'KSvP4AwZG5tYWf1wWuw0meL3QAdJOp',
    'BASE_URL': 'https://api.bitchange.online/api/v1/create_order'
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Token': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    },
    'SHOW_REQUEST_HEADERS': True,
    'JSON_EDITOR': True,
    'USE_SESSION_AUTH': False,
    'api_key': 'Token ae739f0f7b96f79322d00745aaee439ea63c75acfff088c4b5e11a0ee1b578da',
    'is_authenticated': False,
    'is_superuser': False,
    'api_path': "/api/v1/"
}

FRONTEND_URL = 'http://w.beeyonance.exchange'

JET_SIDE_MENU_COMPACT = True

REFERRAL_BONUS_PERCENT = 5

LOGIN_URL = '/login/'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_HOST_USER = 'befree.bingo@yandex.ru'
EMAIL_HOST_PASSWORD = 'Web@123*(_'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


try:
    from .settings_local import *
except ImportError:
    pass
