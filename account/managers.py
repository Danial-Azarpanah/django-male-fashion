from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom manager for the custom User model
    """

    def create_superuser(self, phone, password,
                         **other_fields):
        # Set is_staff, is_superuser, and is_active to True as default
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        return self.create_user(phone=phone, password=password,
                                **other_fields)

    def create_user(self, phone, full_name, password, email=None,
                    **other_fields):
        """
        Creates and saves a User with the given data
        """

        email = self.normalize_email(email)
        user = self.model(phone=phone, full_name=full_name,
                          email=email, **other_fields)
        user.set_password(password)
        user.save()
        return user
