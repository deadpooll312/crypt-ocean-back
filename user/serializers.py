from rest_framework import serializers, exceptions

from user.models import User, AccessToken


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    password_confirm = serializers.CharField()

    def validate(self, attrs):
        self.email_validation(attrs.get('email', None))

        password = attrs.get('password', None)
        password_confirm = attrs.get('password_confirm', None)

        if not password or not password_confirm or password != password_confirm:
            raise exceptions.ValidationError({'password': 'Passwords didn\'t match'})

        return attrs

    def email_validation(self, value):
        if not value:
            raise exceptions.ValidationError('Email required field')

        if User.objects.filter(email=value).exists():
            raise exceptions.ValidationError('Email already used')

        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessToken
        fields = ('token',)
