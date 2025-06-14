# -*- coding: utf-8 -*-

"""
Django settings for web_site project.

Generated by 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import sys


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path = [BASE_DIR] + sys.path


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'n)g+^3r-694n57leg^rfxhe@!yrnb1@ngnx9#)tc)4w08o$#ae'

# SECURITY WARNING: don't run with debug turned on in production!
if os.uname()[1] == 'kaede.nagaokaut.ac.jp':  # 本番環境ではデバッグを外す
    DEBUG = False 
else:
    DEBUG = True

# ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'kaede.nagaokaut.ac.jp', '133.44.120.11']
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cleanup',
    'markdown_deux',
    'users.apps.UsersConfig',
    'public.apps.PublicConfig',
    'report.apps.ReportConfig',
    'paper.apps.PaperConfig',
    'award.apps.AwardConfig',
    'output.apps.OutputConfig',
    'picture.apps.PictureConfig',
    'activity.apps.ActivityConfig',
    'market.apps.MarketConfig',
    
    # wikiで追加
    "wiki.apps.WikiConfig",
    'django.contrib.humanize.apps.HumanizeConfig',
    'django.contrib.sites.apps.SitesConfig',
    'django.contrib.admindocs.apps.AdminDocsConfig',
    'sekizai',
    'sorl.thumbnail',
    "django_nyt.apps.DjangoNytConfig",
    "wiki.plugins.macros.apps.MacrosConfig",
    'wiki.plugins.help.apps.HelpConfig',
    'wiki.plugins.links.apps.LinksConfig',
    "wiki.plugins.images.apps.ImagesConfig",
    "wiki.plugins.attachments.apps.AttachmentsConfig",
    #"wiki.plugins.notifications.apps.NotificationsConfig",
    'wiki.plugins.globalhistory.apps.GlobalHistoryConfig',
    'mptt',
    #"labwiki",
    #"labwiki.LabWikiConfig"
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'web_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),
                 os.path.join(BASE_DIR, "wiki/templates"),
                 ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'web_site.context_processors.path_without_prefix',

                # wikiで追加
                "django.template.context_processors.i18n",
                "django.template.context_processors.tz",
                "sekizai.context_processors.sekizai",
            ],
        },
    },
]

WSGI_APPLICATION = 'web_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.postgresql_psycopg2',
#             'NAME': 'postgres',
#             'USER': 'postgres',
#             'PASSWORD': 'postgres',
#             'HOST': 'db',
#             'PORT': 5432,
#         }
# }


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

if os.uname()[1] == 'kaede.nagaokaut.ac.jp':  # デプロイ時
    # STATIC_ROOT = '/var/www/static' 
    STATIC_ROOT = os.path.join(BASE_DIR, 'static/') 
else:
    STATIC_ROOT = '/static'
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'web_site/static'), )  # アプリ毎以外の静的ファイル

MEDIA_URL = '/media/'
# MEDIA_URL = os.path.join(BASE_DIR, 'media/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 認証にカスタムユーザモデルを採用
AUTH_USER_MODEL = 'users.User'

# if os.uname()[1] == 'kaede.nagaokaut.ac.jp':
#     # デプロイ時のルートディレクトリ
#     URL_PREFIX = '/management'
# else:
#     # ローカル実行時のルートディレクトリ
#     URL_PREFIX = ''
URL_PREFIX = ''

# ログインしていない場合に飛ばすURL
LOGIN_URL = URL_PREFIX + '/admin/login/'

# 国際化関係のファイルの保管場所
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)
# 言語リスト
LANGUAGES = (
  ('ja', 'Japanese'),
  ('en', 'English'),
)

# wiki関連
SITE_ID = 1
WIKI_ACCOUNT_HANDLING = True
WIKI_ANONYMOUS=False

# WARNINGSを消す
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# schemeをhttpsにする
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# X-Frameのoptionの設定
X_FRAME_OPTIONS = 'SAMEORIGIN'
XS_SHARING_ALLOWED_METHODS = ['POST','GET','OPTIONS', 'PUT', 'DELETE']
