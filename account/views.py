from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.shortcuts import redirect
from django.urls import reverse_lazy

from .forms import UserRegisterForm, UserLoginForm


class UserLogin(LoginView):
    """
    View for user login
    """
    template_name = "account/login.html"
    redirect_authenticated_user = True
    fields = "__all__"
    form_class = UserLoginForm

    def get_success_url(self):
        return reverse_lazy("home:main")


class UserRegister(CreateView):
    """
    View for user registration
    """
    template_name = "account/register.html"
    success_url = reverse_lazy("home:main")
    form_class = UserRegisterForm

    def form_valid(self, form):
        user = form.save()
        user.save()
        return redirect("home:main")

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("home:main")
        return super(UserRegister, self).get(*args, **kwargs)

