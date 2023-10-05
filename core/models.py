from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

# override the email field to be unique in the User model.
# in settings.py AUTH_USER_MODEL
class User(AbstractUser):
    email = models.EmailField(unique=True)