from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        TRAINER = "TRAINER", "Trainer"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.TRAINER
    )

    phone = models.CharField(max_length=15, blank=True,unique=True, null=True)

    avatar = models.ImageField(
        upload_to="trainers/",
        blank=True,
        null=True,
        default="trainers/default.png"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"