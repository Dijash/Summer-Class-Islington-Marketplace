import os
from pathlib import Path
# pyrefly: ignore [missing-import]
import dj_database_url
# pyrefly: ignore [missing-import]
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-6x!w@s_dk4&b^#@7+z82%yzl(mqs2ro#!=2t*-ms3o9!ggrv+s')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*']



# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts.apps.AccountsConfig',
    'customer.cart.apps.CartConfig',
    'core.apps.CoreConfig',
    'customer.apps.CustomerConfig',
    'product.apps.ProductConfig',
    'seller.apps.SellerConfig',
    'offers.apps.OffersConfig',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'Marketplace.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Marketplace.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

# 1. This acts as your local default
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 2. Use PostgreSQL in production (e.g., on Render) or if USE_POSTGRES=True
if os.getenv('RENDER') or config('USE_POSTGRES', default=False, cast=bool):
    database_url = config('DATABASE_URL', default=None)
    if database_url:
        if not os.getenv('RENDER') and '@dpg-' in database_url and '.render.com' not in database_url:
            import re
            database_url = re.sub(r'(@dpg-[a-z0-9]+-[a-z0-9]+)(/|\?|$)', r'\1.singapore-postgres.render.com\2', database_url)
        DATABASES['default'] = dj_database_url.parse(database_url, conn_max_age=600)


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'neondb',
#         'USER': 'neondb_owner',
#         'PASSWORD': 'npg_LXSrHwvOcN65',
#         'HOST': 'ep-rough-wildflower-aypyd0mt-pooler.c-5.us-east-2.aws.neon.tech',
#         'PORT': '5432',
#         'OPTIONS': {
#             'sslmode': 'require',
#         },
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'


# Media files (Uploaded by user/admin)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Khalti Payment Gateway Settings
KHALTI_SECRET_KEY = os.getenv('KHALTI_SECRET_KEY', '80007e115d4d421c9d240952044a76fb')
KHALTI_INITIATE_URL = os.getenv('KHALTI_INITIATE_URL', 'https://dev.khalti.com/api/v2/epayment/initiate/')
KHALTI_LOOKUP_URL = os.getenv('KHALTI_LOOKUP_URL', 'https://dev.khalti.com/api/v2/epayment/lookup/')


SOCIALACCOUNT_LOGIN_ON_GET = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('CLIENT_ID', default=config('GOOGLE_CLIENT_ID', default='')),
            'secret': config('CLIENT_SECRET', default=config('GOOGLE_CLIENT_SECRET', default='')),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
            'prompt': 'select_account',
        },
    }
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'

# Email Configuration (OTP & Verification)
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='utsavbhattarai29@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=f'MarketPlace <{EMAIL_HOST_USER}>')