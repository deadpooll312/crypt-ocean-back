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
        fields = ('id', 'coefficient', 'user', 'amount', 'created_at')

    coefficient = CoefficientSerializer()
    user = ProfileSerializer()


class BetCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bet
        fields = ('coefficient_id', 'amount')

    coefficient_id = serializers.IntegerField(read_only=False)

    def validate_coefficient_id(self, value):
        try:
            instance = Coefficient.objects.get(id=value)
        except Coefficient.DoesNotExist:
            raise exceptions.ValidationError('Такой коэффициент не найден')

        return value
