from django.contrib import admin
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

from .models import User, UserBalanceFilRecord, Transaction, BalanceFillConfiguration, UserTraffic, TrafficPercentPaymentLog
from django.contrib.auth.admin import UserAdmin as AbstractUserAdmin
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.admin import Group


# Register your models here.


class UserBalanceFillRecordInline(admin.TabularInline):
    model = UserBalanceFilRecord
    extra = 0
    ordering = ('-created_at',)

    readonly_fields = ['amount', 'currency', 'is_success', 'created_at', 'is_finished']
    exclude = ['error_message', 'token']

    def has_add_permission(self, request, obj=None):
        return False


class TransactionInline(admin.StackedInline):
    model = Transaction
    extra = 0
    fk_name = 'user'
    ordering = ('-created_at',)

    readonly_fields = ['transaction_type', 'amount', 'created_at', 'bonus_from', 'set_date']

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
            'balance',
            'related_referer'
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


@admin.register(UserTraffic)
class UserTrafficAdmin(admin.ModelAdmin):

    list_display = ['ip', 'partner_id', 'click_id', 'site_id', 'created_at', 'source']
    readonly_fields = ['ip', 'partner_id', 'click_id', 'site_id', 'created_at', 'updated_at', 'user_display', 'balance_filled', 'user', 'source']

    fields = ('ip', 'partner_id', 'click_id', 'site_id', 'source', 'created_at', 'updated_at', 'user_display', 'balance_filled')

    list_filter = ['created_at', 'balance_filled', 'source']

    search_fields = ['partner_id', 'click_id', 'ip', 'site_id']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    # def has_change_permission(self, request, obj=None):
    #     return False

    def user_display(self, obj):
        if obj.user:
            url = reverse_lazy('admin:user_user_change', args=(obj.user.id,))
            return mark_safe(f'<a href="{url}#/tab/inline_0/" target="_blank">{obj.user.email}</a>')
        return '-'

    user_display.short_description = "Пользователь"


@admin.register(TrafficPercentPaymentLog)
class TrafficPercentPaymentLogAdmin(admin.ModelAdmin):
    list_display = ['get_traffic_info', 'cost', 'created_at']

    readonly_fields = (
        'get_traffic_info',
        'cost',
        'link',
        'created_at'
    )

    fields = (
        'get_traffic_info',
        'cost',
        'link',
        'created_at'
    )

    def get_traffic_info(self, obj: TrafficPercentPaymentLog):
        return mark_safe('''
        <span>
        (<br />
        &nbps;&nbps;pid = {partner_id},<br/>
        &nbps;&nbps;clickId = {click_id},<br/>
        &nbps;&nbps;subid = {site_id},<br/>
        &nbps;&nbps;source = {src},<br/>
        &nbps;&nbps;ip = {ip}<br />
        )
        </span>
        '''.format(
            partner_id=obj.traffic.partner_id,
            click_id=obj.traffic.click_id,
            site_id=obj.traffic.site_id,
            src=obj.traffic.get_source_display(),
            ip=obj.traffic.ip
        ))

    get_traffic_info.short_description = 'Траффик'

    def has_add_permission(self, request):
        return False


admin.site.unregister(Group)
