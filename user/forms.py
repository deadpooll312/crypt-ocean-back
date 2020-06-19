from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from user.models import User


class LoginForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={
            'class': 'uk-input',
            'placeholder': 'E-mail',
            'autocomplete': 'off'
        }
    ))
    password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={
            'class': 'uk-input',
            'placeholder': 'Пароль',
            'autocomplete': 'off'
        }
    ))

    def clean_email(self):
        value = self.cleaned_data['email']

        if not User.objects.filter(email=value).exists():
            raise ValidationError('Пользователь с таким E-Mail не существует')

        return value
