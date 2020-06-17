# Generated by Django 2.2.7 on 2020-06-17 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0026_trafficpercentpaymentlog_traffic_info'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='balancefillconfiguration',
            options={'verbose_name': 'Настройки сайта', 'verbose_name_plural': 'Настройки сайта'},
        ),
        migrations.AddField(
            model_name='balancefillconfiguration',
            name='page_footer',
            field=models.TextField(blank=True, help_text='Скрипты перед </body>', null=True, verbose_name='FOOTER'),
        ),
        migrations.AddField(
            model_name='balancefillconfiguration',
            name='page_header',
            field=models.TextField(blank=True, help_text='Скрипты <head></head>', null=True, verbose_name='HEADER'),
        ),
    ]
