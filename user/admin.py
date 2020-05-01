from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as AbstractUserAdmin
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.admin import Group


# Register your models here.


@admin.register(User)
class UserAdmin(AbstractUserAdmin):

    list_display = ['email', 'balance', 'date_joined', 'is_active', 'is_staff', 'is_superuser']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name',
            'last_name',
            'username',
            'balance'
        )}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


admin.site.unregister(Group)
