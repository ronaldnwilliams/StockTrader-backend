# Generated by Django 2.0.5 on 2018-06-25 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_accounts', '0032_auto_20180625_1949'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_stock',
            name='daily_balance',
        ),
        migrations.RemoveField(
            model_name='user_stock',
            name='intraday_balance',
        ),
        migrations.AddField(
            model_name='daily_balance',
            name='stock_symbols',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='intraday_balance',
            name='stock_symbols',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
