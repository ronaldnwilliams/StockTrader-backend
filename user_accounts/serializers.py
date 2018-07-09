from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings


from .models import *


class Watch_StockSerializer(serializers.ModelSerializer):

    class Meta:
        model = Watch_Stock
        fields = ('id', 'symbol',)

class User_StockSerializer(serializers.ModelSerializer):

    class Meta:
        model = User_Stock
        fields = ('id', 'symbol', 'quantity', 'purchase_price',
         'purchase_date', 'cost_basis',)

class Daily_BalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Daily_Balance
        fields = ('date', 'balance',)

class PortfolioSerializer(serializers.ModelSerializer):
    stocks = User_StockSerializer(many=True)
    watch_stocks = Watch_StockSerializer(many=True)
    daily_balance = Daily_BalanceSerializer(many=True)

    class Meta:
        model = Portfolio
        fields = ('cash', 'stocks', 'watch_stocks', 'daily_balance',)

class User_AccountSerializer(serializers.ModelSerializer):
    portfolio = PortfolioSerializer()

    class Meta:
        model = User_Account
        fields = ('portfolio', 'joined',)

class UserSerializer(serializers.ModelSerializer):
    user_account = User_AccountSerializer()

    class Meta:
        model = User
        fields = ('username', 'user_account',)


class UserSerializerWithToken(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('token', 'email', 'username', 'password', )

    def get_token(self, obj):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(obj)
        token = jwt_encode_handler(payload)
        return token

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
