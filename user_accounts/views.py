from django.http import HttpResponseRedirect
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, date, time, timedelta
from decimal import *
import requests

from .models import *
from .serializers import *

# django site
@login_required
def index(request):
    user_account = User_Account.objects.get(account_user=request.user)
    context = {'user_account': user_account}
    return render(request, 'user_accounts/index.html', context)

# django site
@login_required
def buy(request):
    user_account = User_Account.objects.get(account_user=request.user)
    portfolio = Portfolio.objects.get(user_account=user_account)
    buy_stock_symbol = request.POST['buy_stock_symbol']
    buy_stock_quantity = int(request.POST['buy_stock_quantity'])
    response = requests.get('https://api.iextrading.com/1.0/stock/{}/quote'.format(buy_stock_symbol))
    quote = response.json()
    last_trade = quote['latestPrice']
    trade_cost = last_trade * buy_stock_quantity
    if portfolio.cash < trade_cost:
        return render(request, 'user_accounts/index.html', {'user_account': user_account, 'error_message': 'Not enough funds. Cash: {} Trade Cost: {}'.format(portfolio.cash, trade_cost)})
    else:
        portfolio.cash -= Decimal(trade_cost)
        bought_stock = User_Stock(
            portfolio=portfolio,
            symbol=buy_stock_symbol.upper(),
            quantity=buy_stock_quantity,
            purchase_price=last_trade
            )
        portfolio.save()
        bought_stock.save()
        return HttpResponseRedirect(reverse('index'))

# django site
@login_required
def sell(request):
    user_account = User_Account.objects.get(account_user=request.user)
    portfolio = Portfolio.objects.get(user_account=user_account)
    sell_stock_id = request.POST['id']
    sell_stock = User_Stock.objects.get(pk=sell_stock_id)
    response = requests.get('https://api.iextrading.com/1.0/stock/{}/quote'.format(sell_stock.symbol))
    quote = response.json()
    last_trade = quote['latestPrice']
    portfolio.cash += sell_stock.quantity * Decimal(last_trade)
    sell_stock.delete()
    portfolio.save()
    return HttpResponseRedirect(reverse('index'))

@api_view(['GET', 'POST', 'DELETE'])
def current_user(request):
    if request.method == 'GET':
        """
        Determine the current user by their token, and return their data
        """
        user = request.user
        daily_balance_update(user)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    if request.method == 'POST':
        """
        From request.user get user and from request.data get symbol and quantity
        If enough cash in portfolio, buy stock
        """
        watch_stock = request.data['watchStock']
        symbol = request.data['symbol']
        user_account = User_Account.objects.get(account_user=request.user)
        portfolio = user_account.portfolio
        # if watch stock true then just add stock to watchlist
        if watch_stock:
            watched_stock = Watch_Stock(portfolio=portfolio, symbol=symbol.upper())
            watched_stock.save()
            portfolio.save()
            serializer = UserSerializer(request.user)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        # else this is a stock purchase
        else:
            try:
                quantity = float(request.data['quantity'])
            except (ValueError, TypeError):
                # TODO: return error
                serializer = UserSerializer(request.user)
                return Response(data=serializer.data, status=status.HTTP_400_BAD_REQUEST)
            response = requests.get('https://api.iextrading.com/1.0/stock/{}/quote'.format(symbol))
            quote = response.json()
            last_trade = quote['latestPrice']
            trade_cost = float(last_trade) * quantity
            #check to see if enough cash
            if portfolio.cash >= trade_cost:
                portfolio.cash -= Decimal(trade_cost)
                try:
                    owned_stock = portfolio.stocks.get(symbol=symbol.upper())
                    avg_price = ((owned_stock.purchase_price * owned_stock.quantity) + (Decimal(last_trade) * Decimal(quantity))) / (owned_stock.quantity + Decimal(quantity))
                    owned_stock.purchase_price = avg_price
                    owned_stock.quantity += Decimal(quantity)
                    owned_stock.save()
                except:
                    bought_stock = User_Stock(
                        portfolio=portfolio,
                        symbol=symbol.upper(),
                        quantity=quantity,
                        purchase_price=last_trade
                        )
                    bought_stock.save()
                # remove from watchlist if there
                try:
                    remove_watch_stock = portfolio.watch_stocks.get(symbol=symbol.upper())
                    remove_watch_stock.delete()
                except:
                    pass
                portfolio.save()
                serializer = UserSerializer(request.user)
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            else:
                serializer = UserSerializer(request.user)
                return Response(data=serializer.data, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        """
        From request.user determine the user and from request.data get stockID
        sell stock
        """
        user_account = User_Account.objects.get(account_user=request.user)
        portfolio = user_account.portfolio
        watch_stock = request.data['watchStock']
        # if watch stock is true then remove watch stock
        if watch_stock:
            watched_stock = portfolio.watch_stocks.get(id=int(request.data['stockID']))
            watched_stock.delete()
            portfolio.save()
            serializer = UserSerializer(request.user)
            return Response(data=serializer.data, status=status.HTTP_202_ACCEPTED)
        # else this is a sell request
        else:
            sell_stock = portfolio.stocks.get(id=int(request.data['stockID']))
            response = requests.get('https://api.iextrading.com/1.0/stock/{}/quote'.format(sell_stock.symbol))
            quote = response.json()
            last_trade = quote['latestPrice']
            portfolio.cash += sell_stock.quantity * Decimal(last_trade)
            sell_stock.delete()
            portfolio.save()
            serializer = UserSerializer(request.user)
            return Response(data=serializer.data, status=status.HTTP_202_ACCEPTED)

def daily_balance_update(user):
    serializer = UserSerializer(user)
    today = date.today()
    user = User.objects.get(username=serializer.data['username'])
    user_account = User_Account.objects.get(account_user=user)
    daily_balances = user_account.portfolio.daily_balance.order_by('date')
    last_balance = daily_balances[len(daily_balances) - 1]
    stocks = user_account.portfolio.stocks.all()
    cash = user_account.portfolio.cash
    last_date = last_balance.date
    if today.weekday() == 0:
        yesterday = today - timedelta(days=2)
    else:
        yesterday = today - timedelta(days=1)
    if yesterday != last_date:
        days_since = today - last_date
        update_dates = get_update_dates(today, days_since, daily_balances)
        charts = get_charts(stocks)
        stock_balances = get_stock_balances(stocks, charts, update_dates)
        for x in update_dates:
            total_stock_bal = Decimal(0.00)
            for y in stock_balances:
                if x.isoformat() == y['date']:
                    total_stock_bal += y['total']
            total_balance = total_stock_bal + cash
            daily_bal = Daily_Balance(
                portfolio=user_account.portfolio,
                date=x,
                balance=total_balance)
            daily_bal.save()

def get_stock_balances(stocks, charts, update_dates):
    stock_balances = []
    for stock in stocks:
        for x in charts[stock.symbol]['chart']:
            for y in update_dates:
                if x['date'] == y.isoformat():
                    stock_total = Decimal(x['close']) * stock.quantity
                    stock_balances.append({
                        'symbol': stock.symbol,
                        'date': x['date'],
                        'total': stock_total,
                    },)
    return stock_balances

def get_update_dates(today, days_since, daily_balances):
    x = 1
    update_dates = []
    trading_holidays = [
        date(2018, 7, 4),
        date(2018, 9, 3),
        date(2018, 11, 22),
        date(2018, 12, 25),
        date(2019, 1, 1),
        date(2019, 1, 21),
        date(2019, 4, 19),
        date(2019, 7, 4)
    ]
    while x <= days_since.days:
        the_date = today - timedelta(days=x)
        if the_date.weekday() < 5 and not daily_balances.filter(date=the_date):
            if the_date not in trading_holidays:
                update_dates.append(the_date)
        x += 1
    return update_dates

def get_charts(stocks):
    if len(stocks):
        # TODO limited to 100 symbols
        stock_URL = ''
        x = 0
        for stock in stocks:
            if x < len(stocks):
                stock_URL += stock.symbol + ','
            else:
                stock_URL += stock.symbol
            x += 1
        # TODO make sure account has logged in within a year
        response = requests.get('https://api.iextrading.com/1.0/stock/market/batch?symbols={}&types=chart&range=1y'.format(stock_URL))
        return response.json()
    else:
        return False

class UserList(APIView):
    """
    Create a new user. It's called 'UserList' because normally we'd have a get
    method here too, for retrieving a list of all User objects.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = UserSerializerWithToken(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username=serializer.data['username'])
            user_account = User_Account.objects.create(account_user=user)
            portfolio = Portfolio.objects.create(user_account=user_account)
            daily_balances = Daily_Balance.objects.create(
                portfolio=portfolio,
                date=date.today(),
                balance=portfolio.cash)
            user_account.save()
            portfolio.save()
            daily_balances.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
