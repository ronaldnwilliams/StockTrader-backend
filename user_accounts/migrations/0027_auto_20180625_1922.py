# Generated by Django 2.0.5 on 2018-06-25 19:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_accounts', '0026_auto_20180625_1711'),
    ]

    operations = [
        migrations.RenameField(
            model_name='daily_balance',
            old_name='balance',
            new_name='cash',
        ),
        migrations.AddField(
            model_name='daily_balance',
            name='daily_stocks',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='daily_stocks', to='user_accounts.User_Stock'),
        ),
    ]
