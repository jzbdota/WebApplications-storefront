import os
from .common import *

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['storefront-yang-8a1f75a68e5d.herokuapp.com']

# lack DATABASE settings