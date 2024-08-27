from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    pass

    # class Meta:
    #     ordering = ['username']

    def __str__(self):
        return self.username


class Subscription(models.Model):
    pass
