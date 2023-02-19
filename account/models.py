from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser):
    """
    Custom User model
    """
    phone = models.CharField(
        max_length=11,
        unique=True,
    )
    email = models.EmailField(
        max_length=255,
        blank=True,
        null=True,
    )
    full_name = models.CharField(
        max_length=50,
    )
    address = models.TextField(
        blank=True,
        null=True,
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
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True


class OTP(models.Model):
    """
    Form for saving temporary user info
    for creating his/her account after
    confirming the OTP code
    """
    phone = models.CharField(max_length=11)
    full_name = models.CharField(max_length=50)
    password = models.CharField(max_length=1000)
    token = models.CharField(max_length=300)
    code = models.CharField(max_length=6)
    expiration = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "OTP code"
        verbose_name_plural = "OTP codes"

    def is_not_expired(self):
        # Check if the OTP code is still valid
        if self.expiration >= timezone.localtime(timezone.now()):
            return True
        return False
