from .common import *

DEBUG = True

SECRET_KEY = 'django-insecure-*lkt=_fo8dmjil%0d)su$_s2aa%2-jnm09=5)jrzo%k!13b=77'

INSTALLED_APPS += [
    'debug_toolbar',
]
MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

if not NOSILK:
    INSTALLED_APPS += [
        'silk',
    ]

    MIDDLEWARE += [
        'silk.middleware.SilkyMiddleware',
    ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'storefront_github',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': 'Pb340121'
    }
}