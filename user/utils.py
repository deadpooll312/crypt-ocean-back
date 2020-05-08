import random

from djmoney.money import Money
from .models import BalanceFillConfiguration


def get_min_fill_amount() -> Money:
    configuration, created = BalanceFillConfiguration.objects.get_or_create(id=1)

    if created:
        configuration.min_fill_amount = Money('750.00', 'RUB')
        configuration.save()

    return configuration.min_fill_amount


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
