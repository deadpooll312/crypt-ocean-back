# Generated by Django 2.2.7 on 2020-05-02 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_userbalancefilrecord_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Имя пользователя'),
        ),
    ]
