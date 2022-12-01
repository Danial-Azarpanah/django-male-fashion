from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser):
    """
    Custom User model
    """
    email = models.EmailField(
        max_length=255,
        unique=True
    )
    phone = models.CharField(
        max_length=11,
        unique=True,
        blank=True,
        null=True
    )
    first_name = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        max_length=40,
        blank=True,
        null=True
    )
    address = models.TextField(
        blank=True,
        null=True
    )
    bio = models.TextField(
        blank=True,
        null=True
    )
    image = models.ImageField(
        upload_to="user_image",
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "phone", "first_name", "last_name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
