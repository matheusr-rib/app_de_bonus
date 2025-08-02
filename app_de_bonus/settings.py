from pathlib import Path
from decouple import config, Csv
import dj_database_url
import os
from decouple import config, UndefinedValueError


BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ Segurança
SECRET_KEY = config('SECRET_KEY', default='unsafe-secret-key')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())

# ✅ Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'campanhas',
    'usuarios',
    'historico.apps.HistoricoConfig',
    'widget_tweaks',
    'storages',  # ✅ Necessário para o Backblaze B2
]

AUTH_USER_MODEL = 'usuarios.Usuario'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'historico.middleware.RequestMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ Para servir estáticos no Render
]

ROOT_URLCONF = 'app_de_bonus.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'app_de_bonus.wsgi.application'

# ✅ Banco de Dados
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='postgres://postgres:1436@localhost:5432/meuappbonus_db'),
        conn_max_age=600
    )
}

# ✅ Validação de senha
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ✅ Localização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True

# ✅ Arquivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ✅ Backblaze B2 - Uploads persistentes
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

try:
    AWS_ACCESS_KEY_ID = config('B2_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('B2_APPLICATION_KEY')
    AWS_STORAGE_BUCKET_NAME = config('B2_BUCKET_NAME')  # 🚨 sem default!
    AWS_S3_ENDPOINT_URL = config('B2_ENDPOINT')
    AWS_DEFAULT_ACL = None
except UndefinedValueError as e:
    raise RuntimeError(f"❌ Variável de ambiente faltando: {e}. Verifique seu .env")

# ✅ Media URL (os arquivos serão servidos via Backblaze)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGOUT_REDIRECT_URL = 'login'
