from django.http import HttpResponseRedirect
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
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
        serializer = UserSerializer(request.user)
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
            quantity = request.data['quantity']
            response = requests.get('https://api.iextrading.com/1.0/stock/{}/quote'.format(symbol))
            quote = response.json()
            last_trade = quote['latestPrice']
            trade_cost = float(last_trade) * float(quantity)
            #check to see if enough cash
            if portfolio.cash >= trade_cost:
                portfolio.cash -= Decimal(trade_cost)
                try:
                    already_own_stock = portfolio.stocks.get(symbol=symbol.upper())
                    already_own_stock.purchase_price = (
                        ((already_own_stock.purchase_price *
                        already_own_stock.quantity) + (last_trade * quantity)) /
                        (already_own_stock + quantity)
                    )
                    already_own_stock.quantity += quantity
                    already_own_stock.save()
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
                return Response({'error_message': 'Not enough cash. Trade cost = {}'.format(trade_cost)}, status=status.HTTP_400_BAD_REQUEST)

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
            user_account.save()
            portfolio.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
