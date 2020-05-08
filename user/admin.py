from django.contrib import admin
from .models import User, UserBalanceFilRecord, Transaction, BalanceFillConfiguration
from django.contrib.auth.admin import UserAdmin as AbstractUserAdmin
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.admin import Group


# Register your models here.


class UserBalanceFillRecordInline(admin.TabularInline):
    model = UserBalanceFilRecord
    extra = 0

    readonly_fields = ['amount', 'currency', 'is_success', 'created_at']
    exclude = ['error_message']

    def has_add_permission(self, request, obj=None):
        return False


class TransactionInline(admin.StackedInline):
    model = Transaction
    extra = 0

    readonly_fields = ['transaction_type', 'amount', 'created_at']

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(AbstractUserAdmin):

    list_display = ['email', 'balance', 'date_joined', 'is_active', 'is_staff', 'is_superuser']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': (
            'full_name',
            'phone_number',
            'username',
            'balance'
        )}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    inlines = (UserBalanceFillRecordInline, TransactionInline)


@admin.register(BalanceFillConfiguration)
class BalanceFillConfigurationAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return self.model.objects.count() < 1


@admin.register(UserBalanceFilRecord)
class BalanceFillRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'currency', 'created_at', 'is_success']
    readonly_fields = ['token', 'error_message', 'user', 'amount', 'currency', 'is_success']


admin.site.unregister(Group)
