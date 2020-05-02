from django.db import models
from djmoney.models.fields import MoneyField
from user.models import User

# Create your models here.


class Coefficient(models.Model):
    class Meta:
        verbose_name_plural = 'Коэффициенты'
        verbose_name = 'Коэффициент'

    date = models.DateField(verbose_name='Дата')
    value = models.FloatField(verbose_name='Значение коэффициента')

    def __str__(self):
        return f'{self.date.__format__("%d.%m.%Y")} => {self.value}'


class Bet(models.Model):
    class Meta:
        verbose_name_plural = 'Ставки'
        verbose_name = 'Ставка'

    is_active = models.BooleanField(default=True, verbose_name='Активно?')
    coefficient = models.ForeignKey(to=Coefficient, on_delete=models.CASCADE, verbose_name='Коэффициент')
    user = models.ForeignKey(to=User, on_delete=models.PROTECT, verbose_name='Пользователь')
    amount = MoneyField(verbose_name='Сумма ставки', max_digits=14, decimal_places=2, default_currency='RUB', default=0)

    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} => {self.coefficient.value} => {self.amount}руб.'
