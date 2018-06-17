from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views
from .views import *


urlpatterns = [
    path('', views.index, name='index'),
    path('buy/', views.buy, name='buy'),
    path('sell/', views.sell, name='sell'),
    path('current_user/', current_user),
    path('users/', UserList.as_view()),
]
