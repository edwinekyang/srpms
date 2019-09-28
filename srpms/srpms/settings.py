"""
Django settings for srpms project.

Generated by 'django-admin startproject' using Django 2.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from datetime import timedelta
import ldap


def get_env(env_name: str, env_file: str = None) -> str:
    """
    Read environment variable, if is empty then try the env_file.

    This function is to support docker secrets, which would normally provide
    a env variable suffix with '_FILE'. The function does not auto suffix in
    case other suffix convention appears.
    """

    env_var = os.environ.get(env_name)

    if env_var:
        pass
    elif env_file:
        try:
            env_var = open(os.environ.get(env_file)).read()
        except FileNotFoundError:
            env_var = ''
    else:
        env_var = ''

    return env_var


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug or test turned on in production!
DEBUG = bool(get_env('DEBUG') == 'True')
TEST = bool(get_env('TEST') == 'True')

# SECURITY WARNING: keep the secret key used in production secret!
if DEBUG:
    SECRET_KEY = 's0bpsthvxi%f9#l9$bi9f4ro!x61m_5)dvslifkgi1$-o59^(n'
else:
    SECRET_KEY = get_env('SECRET_KEY', 'SECRET_KEY_FILE')

# For fixing the CSRF validation error in development
USE_X_FORWARDED_HOST = True
if DEBUG or TEST:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
else:
    ALLOWED_HOSTS = ['srpms.cecs.anu.edu.au']

# Application definition
INSTALLED_APPS = [
    'research_mgt.apps.ResearchMgtConfig',
    'accounts.apps.AccountsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters'
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

ROOT_URLCONF = 'srpms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'srpms.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'srpms',
            'USER': 'srpms',
            'PASSWORD': 'Srpms',
            'HOST': get_env('POSTGRES_HOST') if get_env('POSTGRES_HOST') else 'localhost',
            'PORT': '5432',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': get_env('POSTGRES_DB', 'POSTGRES_DB_FILE'),
            'USER': get_env('POSTGRES_USER', 'POSTGRES_USER_FILE'),
            'PASSWORD': get_env('POSTGRES_PASSWORD', 'POSTGRES_PASSWORD_FILE'),
            'HOST': get_env('POSTGRES_HOST'),
            'PORT': '5432',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators
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

# Customize user model
AUTH_USER_MODEL = 'accounts.SrpmsUser'

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Australia/Canberra'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# REST framework related settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'EXCEPTION_HANDLER': 'srpms.utils.custom_exception_handler'
}

# Disable browsable API in production
if not DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = ('rest_framework.renderers.JSONRenderer',)

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=12),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS384',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Django default
    'accounts.authentication.ANULDAPBackend'
]

# LDAP related settings
AUTH_LDAP_SERVER_URI = get_env('LDAP_ADDR')
AUTH_LDAP_BIND_DN = ""
AUTH_LDAP_BIND_PASSWORD = ""
AUTH_ANU_LDAP_BASE_DN = "ou=People,o=anu.edu.au"

# Use direct bind to reduce load of the LDAP server
AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s," + AUTH_ANU_LDAP_BASE_DN

# Explicitly specify that SRPMS should update user information on every login
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# Cache distinguished names and group memberships for an hour to minimize LDAP traffic.
AUTH_LDAP_CACHE_TIMEOUT = 3600

# Retrieve attributes from LDAP information
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
    "uni_id": "uid",
}

# Should be enable the whole time to ensure test behave normally.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if not DEBUG:
    # HTTPS related settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Prevent browser from identifying content types incorrectly.
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # Activate browser's XSS filtering and help prevent XSS attacks.
    SECURE_BROWSER_XSS_FILTER = True

    # Prevent iframe
    X_FRAME_OPTIONS = 'DENY'

    # TODO: SECURE_HSTS_SECONDS

if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True

    # Disable SSL
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

    # Enable Django debug toolbar during debug
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda x: False,  # Change this to false if you want to disable
        "RENDER_PANELS": True
    }
    INSTALLED_APPS = ['debug_toolbar', ] + INSTALLED_APPS
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware', ] + MIDDLEWARE

    # Log LDAP activities
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"console": {"class": "logging.StreamHandler"}},
        "loggers": {"django_auth_ldap": {"level": "DEBUG", "handlers": ["console"]}},
    }
