from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import ValidationError
from django import forms

from .models import User


class UserRegisterForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email',
                                                            'class': 'input100'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                 'class': 'input100'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password',
                                                                  'class': 'input100'}))

    class Meta:
        model = User
        fields = ["email", "password"]

    def clean(self):
        # Check if the passwords are same
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")

        if password1 != password2:
            raise ValidationError("Passwords don't match", "password_mismatch")

    def clean_password(self):
        # Check whether length of password is equal or larger than 8 characters
        password = self.cleaned_data.get("password")
        if len(password) < 8:
            raise ValidationError('Password length should be more than 8 characters', 'short_password')
        return password

    def clean_email(self):
        # Check that the email for registration is not already taken
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already taken", 'email_taken')
        return email

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """
    The form for user login process
    """
    username = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email',
                                                               'class': 'input100'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                 'class': 'input100'}))


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'is_superuser')
