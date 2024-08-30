from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='users/', blank=True, null=True)

    class Meta:
        ordering = ['username']

    def __str__(self):
        return self.username


# class Subscription(models.Model):
#     pass
