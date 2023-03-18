from django import forms
from django.db.models import Q
from django.core.validators import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField

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
                                                  {"placeholder": "Enter the code sent to your phone",
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


class UserProfileForm(forms.ModelForm):
    """
    Form for user's profile panel
    in which they can modify their info
    """
    full_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Full Name",
                                                              "class": "email-input"}))
    phone = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Phone Number",
                                                          "class": "email-input"}))
    email = forms.EmailField(required=False,
                             widget=forms.EmailInput(attrs={"placeholder": "Email Address",
                                                            "class": "email-input"}))
    address = forms.CharField(required=False,
                              widget=forms.Textarea(attrs={"placeholder": "Your address",
                                                           "class": "comment-area w-100",
                                                           'style': 'background-color: rgba(0, 0, 0, 0.05);'}))
    bio = forms.CharField(required=False,
                          widget=forms.Textarea(attrs={"placeholder": "Your Bio",
                                                       "class": "comment-area w-100",
                                                       'style': 'background-color: rgba(0, 0, 0, 0.05);'}))
    Image = forms.ImageField(required=False, label="تصویر")

    class Meta:
        model = User
        fields = ["full_name", "phone", "email",
                  "address", "bio", "image"]


class PasswordResetPhoneForm(forms.Form):
    phone = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Phone Number",
                                                          "class": "input100"}))

    def clean(self):
        phone = self.cleaned_data.get("phone")
        if not User.objects.filter(phone=phone).exists():
            raise ValidationError("A user with this phone number doesn't exist")


class PasswordResetOtpForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Code",
                                                         "class": "input100"}))


class PasswordResetForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password",
                                                                  "class": "input100"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Retype Password",
                                                                  "class": "input100"}))

    def clean(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if len(password1) < 8:
            raise ValidationError('Password length should be more than 8 characters', 'short_password')
        if password1 != password2:
            raise ValidationError("Passwords don't match", "password_mismatch")


class ChangePasswordForm(forms.Form):
    """
    Form for changing password
    (authenticated users)
    """
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Current Password"}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "New Password"}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Confirm New Password"}))

    def clean(self):
        cd = super().clean()

        new_password1 = cd.get("new_password1")
        new_password2 = cd.get("new_password2")
        if len(new_password1) < 8:
            raise ValidationError("New password should be at least 8 characters")
        elif new_password1 != new_password2:
            raise ValidationError("Passwords don't match")


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'is_superuser')
