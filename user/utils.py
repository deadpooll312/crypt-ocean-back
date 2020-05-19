import random
import threading

from BefreeBingo import settings
from django.core.mail import EmailMessage
from django.template import loader
from djmoney.money import Money
from .models import BalanceFillConfiguration, User, PasswordRecoverToken


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


def send_email_notification(title, body, to, attachment=None):
    email = EmailMessage(title, body=body, to=to)
    email.content_subtype = 'html'
    if attachment:
        email.attach(attachment['file_name'], attachment['content'], attachment['type'])
    email.send()


def send_password_confirm_letter(request, user: User):
    PasswordRecoverToken.objects.filter(user=user).delete()
    token_instance = PasswordRecoverToken.objects.create(user=user)

    template = loader.get_template('password-recover-mail.html')
    context = {
        'url': f'{settings.FRONTEND_URL}/password/restore/?t={token_instance.token}'
    }
    template_message = template.render(request=request, context=context)

    send_email_notification(
        'Сброс пароля | Befree.bingo',
        template_message,
        [user.email]
    )

