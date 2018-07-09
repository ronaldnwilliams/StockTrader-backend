from django.contrib.auth.models import User
from django.db import models


class User_Account(models.Model):
    account_user = models.OneToOneField(User, related_name='user_account', on_delete=models.CASCADE)
    joined = models.DateTimeField(auto_now_add=True)

class Portfolio(models.Model):
    user_account = models.OneToOneField(User_Account, related_name='portfolio', on_delete=models.CASCADE)
    cash = models.DecimalField(max_digits=19, decimal_places=2, default=100000.00)

class Intraday_Balance(models.Model):
    portfolio = models.ForeignKey(Portfolio, related_name='intraday_balance', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    cash = models.DecimalField(max_digits=19, decimal_places=2)
    stock_symbols = models.CharField(max_length=10, null=True)

class Daily_Balance(models.Model):
    portfolio = models.ForeignKey(Portfolio, related_name='daily_balance', on_delete=models.CASCADE)
    date = models.DateField()
    balance = models.DecimalField(max_digits=19, decimal_places=2)

    class Meta:
        ordering = ['date']

class User_Stock(models.Model):
    portfolio = models.ForeignKey(Portfolio, related_name='stocks', on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    quantity = models.DecimalField(max_digits=19, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=19, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.symbol

    @property
    def cost_basis(self):
        return self.quantity * self.purchase_price

class Watch_Stock(models.Model):
    portfolio = models.ForeignKey(Portfolio, related_name='watch_stocks', on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)

    def __str__(self):
        return self.symbol
