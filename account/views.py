import random
from uuid import uuid4

from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View

from .forms import UserRegisterForm, UserLoginForm, CheckOtpForm
from .authentication import CustomBackend
from .models import User, OTP


class UserRegister(View):
    """
    User registration
    by sending OTP code to their phone number
    """

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home:main")
        form = UserRegisterForm
        return render(request, "account/register.html", {"form": form})

    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            phone = cd.get("phone")
            full_name = cd.get("full_name")
            password = cd.get("password")

            token = uuid4().hex
            code = random.randint(100000, 999999)
            # Use a messaging service for sending OTP code
            print(code)
            expiration = timezone.localtime(timezone.now()) + timezone.timedelta(minutes=10)

            OTP.objects.create(phone=phone, full_name=full_name,
                               password=password, token=token,
                               code=code, expiration=expiration)
            return redirect(
                reverse_lazy("account:check-otp") + f"?token={token}"
            )
        return render(request, "account/register.html", {"form": form})


class CheckOtp(View):
    """
    Check if the Otp code
    is still valid and correct
    """

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home:main")
        form = CheckOtpForm
        return render(request, "account/check_otp.html", {"form": form})

    def post(self, request):
        form = CheckOtpForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            token = request.GET.get("token")
            otp = OTP.objects.get(token=token)

            if otp.is_not_expired():

                if cd.get("code") == otp.code:
                    User.objects.create_user(phone=otp.phone, full_name=otp.full_name,
                                        password=otp.password)
                    user = User.objects.get(phone=otp.phone)
                    login(request, user)
                    OTP.objects.filter(phone=user.phone).delete()
                    return redirect("home:main")
                form.add_error("code", "The code you entered is not correct!")
                return render(request, "account/check_otp.html", {"form": form})

            otp.delete()
            form.add_error("code", "The code has expired!")
        return render(request, "account/check_otp.html", {"form": form})


class UserLogin(View):
    """
    View for user login
    using either phone number
    or email
    """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home:main")
        form = UserLoginForm
        return render(request, "account/login.html", {"form": form})

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            username = cd.get("username")
            password = cd.get("password")

            user = CustomBackend.authenticate(request, username, password)

            if user:
                login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                return redirect("home:main")
            else:
                form.add_error("password", "Password incorrect!")
                return render(request, "account/login.html", {"form": form})
        return render(request, "account/login.html", {"form": form})



