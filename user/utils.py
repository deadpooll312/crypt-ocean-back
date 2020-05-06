import random

from djmoney.money import Money
from .models import BalanceFillConfiguration


def get_min_fill_amount() -> Money:
    configuration, created = BalanceFillConfiguration.objects.get_or_create(id=1)

    if created:
        configuration.min_fill_amount = Money('750.00', 'RUB')
        configuration.save()

    return configuration.min_fill_amount
