# Generated by Django 2.0.5 on 2018-06-25 17:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_accounts', '0025_intraday_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intraday_balance',
            name='portfolio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='intraday_balance', to='user_accounts.Portfolio'),
        ),
    ]
