from django.contrib import admin

from .models import *


class PortfolioInline(admin.TabularInline):
    model = Portfolio

class User_AccountAdmin(admin.ModelAdmin):
    inlines = [PortfolioInline,]

admin.site.register(User_Account, User_AccountAdmin)
admin.site.register(User_Stock)
admin.site.register(Watch_Stock)
admin.site.register(Daily_Balance)
admin.site.register(Portfolio)
