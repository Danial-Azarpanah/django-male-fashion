from django.urls import path

from . import views

app_name = "account"
urlpatterns = [
    path("login", views.UserLogin.as_view(), name="login"),
    path("register", views.UserRegister.as_view(), name="register"),
    path("check_otp/", views.CheckOtp.as_view(), name="check-otp"),
    path("profile/", views.UserProfileEdit.as_view(), name="user-profile"),
    path("check-email-otp/", views.CheckEmailOtp.as_view(), name="check-email-otp"),
]