from __future__ import absolute_import, unicode_literals
from celery import task
from .models import *


@task()
def save_all_user_balances():
    user_accounts = User_Account.objects.all()
    for user in user_accounts:
        for balance in user.portfolio.daily_balance.all():
            print(balance)
    return 'all user accounts saved'
