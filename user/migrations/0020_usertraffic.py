# Generated by Django 2.2.7 on 2020-06-12 09:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0019_passwordrecovertoken'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserTraffic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('partner_id', models.CharField(max_length=255, verbose_name='Partner ID (pid)')),
                ('click_id', models.CharField(max_length=255, verbose_name='Click ID (clickid)')),
                ('site_id', models.CharField(blank=True, max_length=255, null=True, verbose_name='Site ID (subid)')),
                ('ip', models.CharField(max_length=16, verbose_name='User IP')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата редактирования')),
                ('balance_filled', models.BooleanField(default=False, verbose_name='Баланс пополнен?')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Трекер траффика',
            },
        ),
    ]
