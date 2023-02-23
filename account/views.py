import random
from uuid import uuid4

from django.views import View
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

from .authentication import CustomBackend
from .models import User, Otp, EmailChangeOtp
from .forms import UserRegisterForm, UserLoginForm, CheckOtpForm, UserProfileForm, CheckEmailOtpForm


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

            Otp.objects.create(phone=phone, full_name=full_name,
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
            otp = Otp.objects.get(token=token)

            if otp.is_not_expired():

                if cd.get("code") == otp.code:
                    User.objects.create_user(phone=otp.phone, full_name=otp.full_name,
                                             password=otp.password)
                    user = User.objects.get(phone=otp.phone)
                    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                    Otp.objects.filter(phone=user.phone).delete()
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


class UserProfileEdit(View):
    """
    View for users to modify their
    profile info
    """

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("account:login")
        form = UserProfileForm(instance=request.user)
        return render(request, "account/user-profile-edit.html", {"form": form})

    def post(self, request):
        user = request.user
        old_email = user.email
        form = UserProfileForm(request.POST, files=request.FILES,
                               instance=request.user)

        if form.is_valid():
            cd = form.cleaned_data
            new_email = cd.get("email")
            if new_email:
                if new_email != old_email:
                    # Check if the new email isn't already used
                    if User.objects.filter(email=new_email).exists():
                        form.add_error("email", "This email is already taken")
                        return render(request, "account/user-profile-edit.html", {"form": form})
                    form.save()
                    user.email = old_email
                    user.save()

                    # Create authentication factors
                    token = uuid4().hex
                    code = random.randint(100000, 999999)
                    print(code)
                    expiration = timezone.localtime(timezone.now()) + timezone.timedelta(minutes=10)

                    # Create a temporary user whose email is bound to change
                    EmailChangeOtp.objects.create(
                        phone=request.user.phone,
                        old_email=old_email,
                        new_email=new_email,
                        code=code,
                        token=token,
                        expiration=expiration,
                    )

                    # Send Otp code to the new email
                    mail_subject = "Authentication code sent to your email!"
                    message = render_to_string("account/change-email-code.html",
                                               {"code": code})
                    to_email = new_email
                    email = EmailMessage(mail_subject, message, to=[to_email])
                    email.send()

                    return redirect(
                        reverse_lazy("account:check-email-otp") + f"?token={token}"
                    )
                form.save()
                messages.add_message(request, messages.SUCCESS, "Info modified successfully")
                return redirect("account:user-profile")
            messages.add_message(request, messages.SUCCESS, "Info modified successfully")
            return redirect("account:user-profile")

        return render(request, "account/user-profile-edit.html", {"form": form})


class CheckEmailOtp(View):

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("home:main")
        form = CheckEmailOtpForm
        return render(request, "account/email-check-otp.html", {"form": form})

    def post(self, request):
        form = CheckEmailOtpForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data

            # Check to see if the code matches
            try:
                unverified_user = EmailChangeOtp.objects.get(token=request.GET.get("token"),
                                                             code=cd.get("code"))
            except:
                form.add_error("code", "The code is incorrect!")
                return render(request, "account/email-check-otp.html", {"form": form})

            # If the OTP code is still valid (not expired)
            if unverified_user.is_not_expired():
                user = User.objects.get(phone=unverified_user.phone)
                user.email = unverified_user.new_email
                try:
                    EmailChangeOtp.objects.filter(phone=request.user.phone).delete()
                except:
                    pass
                user.save()
                # Delete the object created for OTP authentication
                messages.add_message(request, messages.SUCCESS, "Info modified successfully")
                return redirect("account:user-profile")
            else:
                # If OTP code is expired, delete the object associated with it
                try:
                    EmailChangeOtp.objects.filter(phone=request.user.phone).delete()
                except:
                    pass
                form.add_error("code", "Expired, Please try again!")
                return render(request, "account/email-check-otp.html", {"form": form})
        return render(request, "account/email-check-otp.html", {"form": form})
