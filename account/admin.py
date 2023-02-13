from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.contrib import admin

from .forms import UserRegisterForm, UserChangeForm
from .models import User, OTP


class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin
    """
    form = UserChangeForm
    add_form = UserRegisterForm

    search_fields = ('email', 'full_name')
    ordering = ('-created_at',)
    filter_horizontal = ()
    list_filter = ('is_superuser', 'is_staff', 'is_active')
    list_display = ('phone', 'email', 'full_name',
                    'is_superuser', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('phone', 'email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'bio', 'address', 'image')}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'full_name', 'password1', 'password2'),
        }),
    )


admin.site.register(User, UserAdmin)
admin.site.register(OTP)
admin.site.unregister(Group)
