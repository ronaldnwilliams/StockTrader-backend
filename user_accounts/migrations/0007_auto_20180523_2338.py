# Generated by Django 2.0.5 on 2018-05-23 23:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_accounts', '0006_remove_stock_gain_loss'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_account',
            name='account_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='account_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
