from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.contrib import admin

from .forms import UserRegisterForm, UserChangeForm
from .models import User


class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin
    """
    form = UserChangeForm
    add_form = UserRegisterForm

    search_fields = ('email', 'username')
    ordering = ('email',)
    filter_horizontal = ()
    list_filter = ('is_superuser', 'is_staff', 'is_active')
    list_display = ('email', 'first_name', 'last_name',
                    'is_superuser', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'phone', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name',
                                      'bio', 'address', 'image')}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
