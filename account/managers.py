from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom manager for the custom User model
    """

    def create_superuser(self, email, username,
                         first_name, last_name, password,
                         **other_fields):
        # Set is_staff, is_superuser, and is_active to True as default
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        return self.create_user(email=email, username=username,
                                first_name=first_name, last_name=last_name,
                                password=password,
                                **other_fields)

    def create_user(self, email, username,
                    first_name=None, last_name=None,
                    password=None, **other_fields):
        """
        Creates and saves a User with the given data
        """
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, first_name=first_name,
                          last_name=last_name, **other_fields)
        user.set_password(password)
        user.save()
        return user
