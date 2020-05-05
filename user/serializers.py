from rest_framework import serializers, exceptions

from user.models import User, AccessToken, UserBalanceFilRecord


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


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'balance', 'full_name', 'phone_number')


class UserBalanceFillRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBalanceFilRecord
        fields = ('amount', 'currency', 'is_success', 'created_at')
