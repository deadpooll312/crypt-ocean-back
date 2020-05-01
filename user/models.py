from secrets import token_hex

from django.db import models
from django.contrib.auth.models import AbstractUser
from djmoney.models.fields import MoneyField


# Create your models here.


class User(AbstractUser):
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    username = models.CharField(max_length=255, unique=False, null=True, blank=True, verbose_name='Имя пользователя')
    email = models.EmailField(unique=True, verbose_name='E-Mail')

    balance = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class AccessToken(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, default=token_hex)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.token
