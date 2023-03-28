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
from django.contrib.sites.shortcuts import get_current_site

from .authentication import CustomBackend
from .models import User, Otp, ChangedUser, ResetPasswordOtp
from .forms import UserRegisterForm, UserLoginForm, CheckOtpForm \
    , UserProfileForm, PasswordResetPhoneForm, PasswordResetOtpForm \
    , PasswordResetForm, ChangePasswordForm


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
        if request.user.is_authenticated or not request.GET.get("token"):
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
            messages.add_message(request, messages.ERROR, "The code is expired")
            return redirect("account:register")
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
        old_phone = user.phone
        old_email = user.email
        form = UserProfileForm(request.POST, files=request.FILES,
                               instance=request.user)

        if form.is_valid():

            cd = form.cleaned_data
            new_phone = cd.get("phone")
            new_email = cd.get("email")
            code = random.randint(100000, 999999)
            expiration = timezone.localtime(timezone.now()) + timezone.timedelta(minutes=10)

            changed_user = ChangedUser.objects.create(
                user_id=user.id,
                phone=new_phone,
                email=new_email,
                code=code,
                expiration=expiration
            )

            # If user wants to change his/her email address
            if new_email:
                if new_email != old_email:
                    # Check whether new email isn't already taken
                    if User.objects.filter(email=new_email):
                        form.add_error("email", "Email is already taken")
                        return render(request, "account/user-profile-edit.html", {"form": form})

                    # Save the info except new email (needs authorization)
                    form.save()
                    user.email = old_email
                    user.phone = old_phone
                    user.save()

                    # Create token for email change
                    changed_user.phone_change_successfull = True
                    changed_user.email_token = uuid4().hex
                    changed_user.save()

                    # Send an email containing authorization link to user
                    current_site = get_current_site(self.request)  # to get the domain of the current site
                    mail_subject = 'Email change link sent!'
                    message = render_to_string('account/email-change-link.html', {
                        'user': user,
                        'url': str(current_site.domain)
                               + reverse_lazy("account:change-email")
                               + f"?token={changed_user.email_token}",
                    })
                    to_email = form.cleaned_data.get('email')
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()

                    messages.add_message(request, messages.SUCCESS, f"Link is sent to {new_email}")
                else:
                    changed_user.email_change_successfull = True
                    changed_user.save()
            else:
                changed_user.email_change_successfull = True
                changed_user.phone_change_successfull = True
                changed_user.save()
                form.save()
                user.phone = old_phone
                user.save()

            # Check if only the phone is going to change (not email)
            if new_phone != old_phone:

                # Save the info except the new phone (needs authorization)
                form.save()
                user.phone = old_phone
                user.save()

                # Create token for phone change
                changed_user.phone_change_successfull = False
                changed_user.phone_token = uuid4().hex
                changed_user.save()

                # This line has to be converted to a messaging service
                print(code)

                return redirect(
                    reverse_lazy("account:change-phone") + f"?token={changed_user.phone_token}"
                )

            # If neither email nor phone number are modified
            if (new_phone == old_phone and new_email == old_email) or (not new_email and new_email != old_email):
                changed_user.delete()
                form.save()
                messages.add_message(request, messages.SUCCESS, "Info modified successfully")
                return render(request, "account/user-profile-edit.html", {"form": form})
        return render(request, "account/user-profile-edit.html", {"form": form})


class ChangePhone(View):
    """
    View for changing phone number
    based on OTP code
    """
    def get(self, request):
        if not request.user.is_authenticated or not request.GET.get("token"):
            return redirect("home:main")
        form = CheckOtpForm
        return render(request, "account/check_otp.html", {"form": form})

    def post(self, request):
        form = CheckOtpForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            token = request.GET.get("token")

            # Try finding a user with matching token and code
            try:
                changed_user = ChangedUser.objects.get(phone_token=token, code=cd.get("code"))
            # Return error if not found
            except:
                messages.add_message(request, messages.ERROR, "Code is incorrect")
                return redirect(
                    reverse_lazy("account:change-phone") + f"?token={token}"
                )

            # Check whether the code is expired
            if changed_user.is_not_expired():
                user = User.objects.get(id=changed_user.user_id)
                user.phone = changed_user.phone
                user.save()
            else:
                messages.add_message(request, messages.ERROR, "Expired! Please try again")
                changed_user.delete()
                return redirect("account:user-profile")

            changed_user.phone_change_successfull = True
            changed_user.save()

            # If the fields that needed authorization are changed successfully, delete the changed_user object
            if changed_user.phone_change_successfull and changed_user.email_change_successfull:
                changed_user.delete()

            if not changed_user.email_change_successfull:
                messages.add_message(request, messages.SUCCESS, f"Link is sent to {changed_user.email}")
            else:
                messages.add_message(request, messages.SUCCESS, "Profile modified successfully")
            return redirect("account:user-profile")

        return redirect("home:main")


class ChangeEmail(View):
    """
    View for changing email
    based on a link sent to email
    """

    def get(self, request):
        token = request.GET.get("token")

        # Try to find a changed user with matching token
        try:
            changed_user = ChangedUser.objects.get(email_token=token)
        except:
            messages.add_message(request, messages.ERROR, "Some error occured! Please try again")
            return redirect("account:user-profile")

        if changed_user.is_not_expired():
            user = User.objects.get(id=changed_user.user_id)
            user.email = changed_user.email
            user.save()
        else:
            messages.add_message(request, messages.ERROR, "Expired! Please try again")
            changed_user.delete()
            return redirect("account:user-profile")
        form = UserProfileForm(instance=request.user)
        form.email = user.email
        changed_user.email_change_successfull = True
        changed_user.save()
        if changed_user.email_change_successfull and changed_user.phone_change_successfull:
            changed_user.delete()
        messages.add_message(request, messages.SUCCESS, "Profile modified successfully")
        return redirect("account:user-profile")


class PasswordResetPhone(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home:main")
        form = PasswordResetPhoneForm
        return render(request, "account/reset-password-phone.html", {"form": form})

    def post(self, request):
        form = PasswordResetPhoneForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            token = uuid4().hex
            code = random.randint(100000, 999999)
            print(code)
            expiration = timezone.localtime(timezone.now()) + timezone.timedelta(minutes=10)

            ResetPasswordOtp.objects.create(phone=cd.get("phone"),
                                            token=token,
                                            code=code,
                                            expiration=expiration)

            return redirect(
                reverse_lazy("account:password-reset-otp") + f"?token={token}"
            )
        return render(request, "account/reset-password-phone.html", {"form": form})


class PasswordResetCheckOtp(View):
    def get(self, request):
        if request.user.is_authenticated or not request.GET.get("token"):
            return redirect("home:main")
        form = PasswordResetOtpForm
        return render(request, "account/reset-password-otp.html", {"form": form})

    def post(self, request):
        form = PasswordResetOtpForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            token = request.GET.get("token")
            password_reset_user = ResetPasswordOtp.objects.get(token=token)
            code = cd.get("code")

            if password_reset_user.is_not_expired():
                if password_reset_user.code == code:
                    password_reset_user.phone_confirmed = True
                    password_reset_user.save()
                    return redirect(
                        reverse_lazy("account:password-reset") + f"?token={token}"
                    )
                form.add_error("code", "The code is incorrect")
                return render(request, "account/reset-password-otp.html", {"form": form})
            messages.add_message(request, messages.ERROR, "Expired! Please try again")
            password_reset_user.delete()
            return redirect("account:password-reset-phone")
        return render(request, "account/reset-password-otp.html", {"form": form})


class PasswordReset(View):

    def get(self, request):
        if request.user.is_authenticated or not request.GET.get("token"):
            return redirect("home:main")
        form = PasswordResetForm
        return render(request, "account/reset-password.html", {"form": form})

    def post(self, request):
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            token = request.GET.get("token")

            try:
                password_reset_user = ResetPasswordOtp.objects.get(token=token)
                if not password_reset_user.phone_confirmed:
                    messages.add_message(request, messages.ERROR, "First you should confirm your phone number")
                    return redirect(
                        reverse_lazy("account:password-reset-otp") + f"?token={token}"
                    )
            except:
                messages.add_message(request, messages.ERROR, "Something went wrong! Try again")
                return redirect("account:password-reset-phone")

            if password_reset_user.is_not_expired():
                password1 = cd.get("password1")

                user = User.objects.get(phone=password_reset_user.phone)
                user.set_password(password1)
                user.save()
                login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                password_reset_user.delete()
                messages.add_message(request, messages.SUCCESS, "Your password was changed successfully")
                return redirect("account:user-profile")
            messages.add_message(request, messages.ERROR, "Expired! Please try again")
            password_reset_user.delete()
            return redirect("account:password-reset-phone")
        return render(request, "account/reset-password.html", {"form": form})


class ChangePasswordView(View):
    """
    View for the process of changing
    the password (while being authenticated)
    """

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("account:login")
        form = ChangePasswordForm
        return render(request, "account/change-password.html", {"form": form})

    def post(self, request):
        form = ChangePasswordForm(request.POST, request=request)
        if form.is_valid():
            cd = form.cleaned_data
            user = request.user
            new_password = cd.get("new_password1")
            user.set_password(new_password)
            user.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.add_message(request, messages.SUCCESS, "Password changed successfully")
            return redirect("account:user-profile")
        return render(request, "account/change-password.html", {"form": form})





