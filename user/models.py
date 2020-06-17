import uuid
from secrets import token_hex

from django.utils.safestring import mark_safe
from djmoney.money import Money

from user.constants import TRANSACTION_TYPE_CHOICES, FILL_TRANSACTION
from django.db import models
from django.contrib.auth.models import AbstractUser
from bets.utils import get_random_number, get_random_string
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

    def add_balance(self, amount: Money, transaction_type=FILL_TRANSACTION, bonus_from: 'User' = None, set_date=None):
        self.balance += amount

        Transaction.objects.create(
            user=self,
            amount=abs(amount),
            transaction_type=transaction_type,
            bonus_from=bonus_from,
            set_date=set_date
        )

        self.save()


class AccessToken(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, default=token_hex)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.token


class PasswordRecoverToken(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, default=token_hex)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return self.token


# TODO: Typo error ;(
class UserBalanceFilRecord(models.Model):
    class Meta:
        verbose_name_plural = 'История пополнения баланса'
        verbose_name = 'Элемент истории'

    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='Пользователь')
    amount = models.CharField(max_length=255, verbose_name='Сумма пополнения')
    currency = models.CharField(max_length=255, verbose_name='Валюта')

    is_success = models.BooleanField(default=False, verbose_name='Успешно пополнено?')
    error_message = models.TextField(verbose_name='Сообщение', null=True, blank=True)

    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    token = models.CharField(max_length=255, verbose_name='Токен проверки', default=get_random_string, unique=True)
    is_finished = models.BooleanField(default=False, verbose_name='Оплата проведена до конца?')

    def __str__(self):
        return self.amount


class Transaction(models.Model):
    class Meta:
        verbose_name_plural = 'Транзакции пользователя'
        verbose_name = 'Транзакция'

    user = models.ForeignKey(to=User, on_delete=models.PROTECT, verbose_name='Пользователь', related_name='transactions')
    transaction_type = models.CharField(max_length=255, verbose_name='Тип транзакции', choices=TRANSACTION_TYPE_CHOICES)
    amount = MoneyField(max_digits=14, decimal_places=2, default_currency='RUB', default=0, verbose_name='Сумма')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    set_date = models.DateField(verbose_name='Дата ставки', null=True, blank=True)
    bonus_from = models.ForeignKey(to=User, on_delete=models.SET_NULL, verbose_name='От реферала', null=True, blank=True, related_name='bonus_transactions')

    def __str__(self):
        _ = f'[{self.user.email}] ({self.created_at.__format__("%d.%m.%Y %H:%M")})'

        if self.transaction_type == FILL_TRANSACTION:
            return f'{_} +{self.amount}'

        return f'{_} -{self.amount}'


class BalanceFillConfiguration(models.Model):
    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    min_fill_amount = MoneyField(max_digits=14, decimal_places=2, default_currency='RUB', default=0, verbose_name='Минимальная сумма пополнения')

    page_header = models.TextField(verbose_name='HEADER', null=True, blank=True, help_text='Скрипты &lt;head&gt;&lt;/head&gt;')
    page_footer = models.TextField(verbose_name='FOOTER', null=True, blank=True, help_text='Скрипты перед &lt;/body&gt;')

    def __str__(self):
        return 'Настройка пополнений баланса'


class UserTraffic(models.Model):
    class Meta:
        verbose_name_plural = 'Трекер траффика'
        verbose_name = 'Пользователь'

    partner_id = models.CharField(max_length=255, verbose_name='Partner ID (pid)')
    click_id = models.CharField(max_length=255, verbose_name='Click ID (clickid)')
    site_id = models.CharField(max_length=255, verbose_name='Site ID (subid)', null=True, blank=True)
    source = models.CharField(max_length=10, default='mkt', verbose_name='Source (src)', choices=(
        ('mkt', 'Pixel'),
        ('cityads', 'CityAds')
    ))

    ip = models.CharField(max_length=16, verbose_name='User IP')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата редактирования')

    user = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    balance_filled = models.BooleanField(default=False, verbose_name='Баланс пополнен?')

    def __str__(self):
        return f'{self.ip}: {{"partner_id": {self.partner_id}, "click_id": {self.click_id}}}'


class TrafficPercentPaymentLog(models.Model):
    class Meta:
        verbose_name = 'Лог выплат на траффик'
        verbose_name_plural = 'Лог выплат на траффик'

    traffic = models.ForeignKey(to=UserTraffic, on_delete=models.PROTECT, verbose_name='Пользователь')
    cost = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', default=0)
    link = models.TextField(verbose_name='Ссылка')
    traffic_info = models.TextField(verbose_name='Инфо о траффике', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return self.traffic.ip

    def get_traffic_info(self):
        if self.traffic_info:
            return mark_safe(self.traffic_info)

        return mark_safe('''
                <span>
                <b>Запись о траффике отсутствует. Предоставлены последние найденные записи:</b><br />
                pid = {partner_id},<br/>
                clickId = {click_id},<br/>
                subid = {site_id},<br/>
                source = {src},<br/>
                ip = {ip}<br />
                </span>
                '''.format(
            partner_id=self.traffic.partner_id,
            click_id=self.traffic.click_id,
            site_id=self.traffic.site_id,
            src=self.traffic.get_source_display(),
            ip=self.traffic.ip
        ))
