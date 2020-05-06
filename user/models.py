from secrets import token_hex

from djmoney.money import Money

from user.constants import TRANSACTION_TYPE_CHOICES, FILL_TRANSACTION
from django.db import models
from django.contrib.auth.models import AbstractUser
from bets.utils import get_random_number
from djmoney.models.fields import MoneyField


# Create your models here.


class User(AbstractUser):
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    username = models.CharField(max_length=255, unique=False, blank=True, verbose_name='Имя пользователя', default='')
    email = models.EmailField(unique=True, verbose_name='E-Mail')

    full_name = models.CharField(max_length=255, verbose_name='Полное имя', null=True, blank=True)
    phone_number = models.CharField(max_length=255, verbose_name='Номер телефона', null=True, blank=True)

    balance = MoneyField(max_digits=14, decimal_places=2, default_currency='RUB', default=0)

    promo_code = models.CharField(max_length=20, verbose_name='Промокод для регистрации', default=get_random_number, unique=True)
    related_referer = models.ForeignKey(to='User', on_delete=models.SET_NULL, null=True, blank=True, related_name='referral')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_full_name(self):
        if self.full_name:
            return self.full_name
        return super(User, self).get_full_name()


class AccessToken(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, default=token_hex)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.token


class UserBalanceFilRecord(models.Model):
    class Meta:
        verbose_name_plural = 'История пополнения баланса'
        verbose_name = 'Элемент истории'

    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='Пользователь')
    amount = models.CharField(max_length=255, verbose_name='Сумма пополнения')
    currency = models.CharField(max_length=255, verbose_name='Валюта')

    is_success = models.BooleanField(default=False, verbose_name='Успешно пополнено!')
    error_message = models.TextField(verbose_name='Текст ошибки', null=True, blank=True)

    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)

    def __str__(self):
        return self.amount

    def save(self, *args, **kwargs):
        super(UserBalanceFilRecord, self).save(*args, **kwargs)

        if self.is_success:
            Transaction.objects.create(
                user=self.user,
                transaction_type=FILL_TRANSACTION,
                amount=Money(self.amount, 'RUB')
            )


class Transaction(models.Model):
    class Meta:
        verbose_name_plural = 'Транзакции пользователя'
        verbose_name = 'Транзакция'

    user = models.ForeignKey(to=User, on_delete=models.PROTECT, verbose_name='Пользователь')
    transaction_type = models.CharField(max_length=255, verbose_name='Тип транзакции', choices=TRANSACTION_TYPE_CHOICES)
    amount = MoneyField(max_digits=14, decimal_places=2, default_currency='RUB', default=0, verbose_name='Сумма')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        _ = f'[{self.user.email}] ({self.created_at.__format__("%d.%m.%Y %H:%M")})'

        if self.transaction_type == FILL_TRANSACTION:
            return f'{_} +{self.amount}'

        return f'{_} -{self.amount}'


class BalanceFillConfiguration(models.Model):
    class Meta:
        verbose_name = 'Настройка пополнений баланса'
        verbose_name_plural = 'Настройка пополнений баланса'

    min_fill_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='RUB', default=0, verbose_name='Минимальная сумма пополнения')

    def __str__(self):
        return 'Настройка пополнений баланса'
