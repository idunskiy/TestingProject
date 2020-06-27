from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    image = models.ImageField(default='pics/default.jpg', upload_to='pics')