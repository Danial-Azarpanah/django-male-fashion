from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

app_name = "account"
urlpatterns = [
    path("login", views.UserLogin.as_view(), name="login"),
    path("register", views.UserRegister.as_view(), name="register"),
    path("logout", LogoutView.as_view(next_page="home:main"), name="logout"),
    path("check-otp/", views.CheckOtp.as_view(), name="check-otp"),
    path("profile/", views.UserProfileEdit.as_view(), name="user-profile"),
    path("change-email/", views.ChangeEmail.as_view(), name="change-email"),
    path("change-phone/", views.ChangePhone.as_view(), name="change-phone"),
    path("password-reset-phone/", views.PasswordResetPhone.as_view(), name="password-reset-phone"),
    path("password-reset-otp/", views.PasswordResetCheckOtp.as_view(), name="password-reset-otp"),
    path("password-reset/", views.PasswordReset.as_view(), name="password-reset"),
]
