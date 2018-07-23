from django.contrib import admin

from .models import *

# class User_StockInline(admin.TabularInline):
#     model = User_Stock

class PortfolioInline(admin.TabularInline):
    model = Portfolio
    # inlines = [User_StockInline, ]

class User_AccountAdmin(admin.ModelAdmin):
    fields = ['account_user']
    inlines = [PortfolioInline, ]

admin.site.register(User_Account, User_AccountAdmin)
# admin.site.register(User_Stock)
# admin.site.register(Watch_Stock)
admin.site.register(Daily_Balance)
admin.site.register(Portfolio)
