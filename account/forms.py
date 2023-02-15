from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.validators import ValidationError
from django.db.models import Q
from django import forms

from .models import User


class UserRegisterForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Phone Number',
                                                          'class': 'input100'}))
    full_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Full Name',
                                                              'class': 'input100'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                 'class': 'input100'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password',
                                                                  'class': 'input100'}))

    class Meta:
        model = User
        fields = ["phone", "full_name", "password"]

    def clean(self):
        # Check if the phone number isn't already registered
        phone = self.cleaned_data.get("phone")
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("This phone number is already taken!", "already_used_phone")

        # Check if the passwords are same and longer than 8 characters
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if len(password1) < 8:
            raise ValidationError('Password length should be more than 8 characters', 'short_password')
        if password1 != password2:
            raise ValidationError("Passwords don't match", "password_mismatch")

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CheckOtpForm(forms.Form):
    """
    Form for saving temporary user info
    for creating his/her account after
    confirming the OTP code
    """
    code = forms.CharField(widget=forms.TextInput(attrs=
                                                  {"placeholder": "Enter 6 digit code",
                                                   "class": "input100"}))


class UserLoginForm(forms.Form):
    """
    The form for user login process
    using either email or phone number
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Email or Phone',
                                                             'class': 'input100'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                 'class': 'input100'}))

    def clean(self):
        # Check if there is a user with matching email/phone number
        username = self.cleaned_data.get("username")
        if not User.objects.filter(Q(phone=username) | Q(email=username)).exists():
            raise ValidationError("No such user available!", "user_not_found")


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'is_superuser')
