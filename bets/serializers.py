import datetime

from django.utils import timezone
from rest_framework import serializers, exceptions
from .models import Coefficient, Bet
from user.serializers import ProfileSerializer


class CoefficientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coefficient
        fields = ('id', 'date', 'value')


class BetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bet
        fields = ('id', 'date', 'user', 'amount', 'created_at')

    user = ProfileSerializer()


class BetCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bet
        fields = ('amount', 'date')

    # coefficient_id = serializers.IntegerField(read_only=False)

    def validate_date(self, value: 'datetime.date'):
        if value <= datetime.date.today():
            raise exceptions.ValidationError('Эта дата уже не актуальна')
        return value
