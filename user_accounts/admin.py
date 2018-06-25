from django.contrib import admin

from .models import *


class Daily_BalanceInline(admin.TabularInline):
    model = Daily_Balance

class Intraday_BalanceInline(admin.TabularInline):
    model = Intraday_Balance

class Watch_StockInline(admin.TabularInline):
    model = Watch_Stock

class User_StockInline(admin.TabularInline):
    model= User_Stock

class PortfolioInline(admin.TabularInline):
    model = Portfolio

    inlines = [User_StockInline, Watch_StockInline, Intraday_BalanceInline,
    Daily_BalanceInline,]

class User_AccountAdmin(admin.ModelAdmin):
    inlines = [PortfolioInline,]

admin.site.register(User_Account, User_AccountAdmin)
admin.site.register(User_Stock)
admin.site.register(Watch_Stock)
admin.site.register(Daily_Balance)
admin.site.register(Intraday_Balance)
admin.site.register(Portfolio)
