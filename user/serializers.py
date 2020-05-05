from djmoney.money import Money
from rest_framework import serializers, exceptions
import decimal
from user.models import User, AccessToken, UserBalanceFilRecord, Transaction
from user.utils import get_min_fill_amount


class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    password = serializers.CharField()

    def validate_email(self, value):
        if not value:
            raise exceptions.ValidationError('Email обязательна к заполнению')

        if User.objects.filter(email=value).exists():
            raise exceptions.ValidationError('Этот Email уже используется')

        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessToken
        fields = ('token',)


class FillBalanceSerializer(serializers.Serializer):
    balance = serializers.CharField()

    def validate_balance(self, value):
        try:
            value = decimal.Decimal(value)
        except decimal.ConversionSyntax:
            raise exceptions.ValidationError('Не удалось распознать число')

        if Money(value, 'RUB') < get_min_fill_amount():
            raise exceptions.ValidationError(f'Минимальная сумма пополнения: {get_min_fill_amount()}')

        return str(value)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'balance', 'full_name', 'phone_number')


class UserBalanceFillRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBalanceFilRecord
        fields = ('amount', 'currency', 'is_success', 'created_at')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('transaction_type', 'amount', 'created_at')


class BalanceFillResponseDataSerializer(serializers.Serializer):
    session_id = serializers.CharField()


class BalanceFillResponseSerializer(serializers.Serializer):
    data = BalanceFillResponseDataSerializer()
    id = serializers.IntegerField()
    method = serializers.CharField()
    url = serializers.CharField()
