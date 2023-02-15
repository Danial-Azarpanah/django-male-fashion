from django.contrib.auth.hashers import check_password
from django.db.models import Q

from .models import User


class CustomBackend(object):
    """
    Custom authentication backend to use for
    logging in with email/phone number
    """
    @staticmethod
    def authenticate(request, username=None, password=None):
        try:
            user = User.objects.get(
                Q(phone=username) | Q(email=username)
            )

        except User.DoesNotExist:
            return None

        if user and user.password == password:
            return user
        elif user and check_password(password, user.password):
            return user

        return None

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None