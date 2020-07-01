from typing import Optional

from djmoney.money import Money
from rest_framework import serializers, exceptions
import decimal
from user.models import User, AccessToken, UserBalanceFilRecord, Transaction, PasswordRecoverToken, UserTraffic, BalanceFillConfiguration
from user.utils import get_min_fill_amount


class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    email = serializers.EmailField()
    phone_number = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    password = serializers.CharField()
    promo_code = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    def validate_email(self, value):
        if not value:
            raise exceptions.ValidationError('Email обязательна к заполнению')

        if User.objects.filter(email=value).exists():
            raise exceptions.ValidationError('Этот Email уже используется')

        return value

    def validate_promo_code(self, value) -> Optional[User]:
        if value:
            user = User.objects.filter(promo_code=value).first()

            if not user:
                raise exceptions.ValidationError('Неправильный промокод')

            return user

        return None


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
        fields = ('email', 'balance', 'full_name', 'phone_number', 'promo_code', 'related_referer')


class UserBalanceFillRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBalanceFilRecord
        fields = ('amount', 'currency', 'is_success', 'created_at', 'error_message', 'is_finished')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('transaction_type', 'amount', 'created_at', 'set_date', 'bonus_from')

    bonus_from = ProfileSerializer()


class BalanceFillResponseDataSerializer(serializers.Serializer):
    session_id = serializers.CharField()


class BalanceFillResponseSerializer(serializers.Serializer):
    amount = serializers.CharField()
    currency = serializers.CharField()
    error_code = serializers.IntegerField()
    error_message = serializers.CharField()
    invoice_type = serializers.CharField()
    order_id = serializers.IntegerField()
    order_status = serializers.CharField()
    payment_token = serializers.CharField()
    payment_url = serializers.CharField()
    result = serializers.CharField()
    return_url = serializers.CharField()
    timestamp = serializers.IntegerField()


class BalanceFillConfirmSerializer(serializers.Serializer):
    shop_order_id = serializers.CharField()
    status = serializers.ChoiceField(choices=(('success', 'Успех'), ('failure', 'Не удача')), allow_blank=True, allow_null=True, required=False)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('full_name', 'email', 'phone_number')


class RecoverPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not value:
            raise exceptions.ValidationError('Email required')

        if not User.objects.filter(email=value).exists():
            raise exceptions.ValidationError('User not found')

        return value


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    confirm_password = serializers.CharField()
    check_token = serializers.CharField()

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise exceptions.ValidationError({
                'password': ['Пароли не совпадают']
            })
        return attrs

    def validate_check_token(self, value):
        try:
            token_instance = PasswordRecoverToken.objects.get(token=value)
        except PasswordRecoverToken.DoesNotExist:
            raise exceptions.ValidationError('Токен проверки не валидный')

        if token_instance.is_used:
            raise exceptions.ValidationError('Токен устарел')

        return token_instance


class UserTrafficSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTraffic
        fields = ('partner_id', 'click_id', 'site_id', 'source')


class CommonSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceFillConfiguration
        fields = ('page_header', 'page_footer')
