from django.views import generic
from django.utils.decorators import method_decorator
from djmoney.money import Money
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, exceptions
from rest_framework.response import Response

from user.constants import BET_TRANSACTION
from user.models import Transaction
from user.permissions import IsAuthenticated
from .serializers import CoefficientSerializer
from .models import Coefficient, Bet
from bets.serializers import BetCreationSerializer, BetSerializer

# Create your views here.


class IndexView(generic.TemplateView):
    template_name = 'coming-soon.html'


@method_decorator(swagger_auto_schema(
    operation_summary='Список коэффициентов'
), name='get')
class CoefficientListAPIView(generics.ListAPIView):

    serializer_class = CoefficientSerializer
    queryset = Coefficient.objects.all()

    permission_classes = (IsAuthenticated,)


@method_decorator(swagger_auto_schema(
    query_serializer=BetCreationSerializer(),
    responses={
        201: BetSerializer()
    },
    operation_description='Пользователь берется из токена',
    operation_summary='Сделать ставку'
), name='post')
class MakeBetAPIView(generics.CreateAPIView):

    serializer_class = BetCreationSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer) -> Bet:
        if self.request.user.balance < Money(serializer.validated_data.get('amount'), 'RUB'):
            raise exceptions.ValidationError({'amount': 'У вас не достаточно средств'})

        instance: Bet = serializer.save(user=self.request.user)
        self.request.user.balance = self.request.user.balance - Money(serializer.validated_data.get('amount'), 'RUB')
        self.request.user.save()

        Transaction.objects.create(
            user=self.request.user,
            transaction_type=BET_TRANSACTION,
            amount=instance.amount
        )

        return instance

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(BetSerializer(instance=instance).data, status=status.HTTP_201_CREATED, headers=headers)
