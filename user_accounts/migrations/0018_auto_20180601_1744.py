# Generated by Django 2.0.5 on 2018-06-01 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_accounts', '0017_portfolio_cash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfolio',
            name='cash',
            field=models.DecimalField(decimal_places=2, default=100000.0, max_digits=19),
        ),
    ]
