# Generated by Django 2.2.7 on 2020-06-12 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0020_usertraffic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertraffic',
            name='ip',
            field=models.CharField(max_length=16, unique=True, verbose_name='User IP'),
        ),
    ]