# Generated by Django 2.0.5 on 2018-05-29 17:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_accounts', '0015_auto_20180525_2242'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='portfolio',
            name='cash',
        ),
    ]
