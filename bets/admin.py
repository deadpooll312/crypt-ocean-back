from django.contrib import admin
from .models import Coefficient, Bet

# Register your models here.


@admin.register(Coefficient)
class CoefficientAdmin(admin.ModelAdmin):
    list_display = ['date', 'value']


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ['coefficient', 'user', 'amount', 'created_at', 'is_active']

    search_fields = ['coefficient', 'amount']
    list_filter = ['is_active']
