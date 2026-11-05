from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('agent', 'Support Agent'),
        ('admin', 'Administrator'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer'
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        # Django superusers must also have the application's admin role.
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
