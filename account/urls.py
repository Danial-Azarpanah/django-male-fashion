from django.urls import path

from . import views

app_name = "account"
urlpatterns = [
    path("login", views.UserLogin.as_view(), name="login"),
    path("register", views.UserRegister.as_view(), name="register"),
    path("check-otp/", views.CheckOtp.as_view(), name="check-otp"),
    path("profile/", views.UserProfileEdit.as_view(), name="user-profile"),
    path("change-email/", views.ChangeEmail.as_view(), name="change-email"),
    path("change-phone/", views.ChangePhone.as_view(), name="change-phone"),
]