from typing import Optional

import requests
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import generics, status, views, exceptions
from rest_framework.response import Response

from BefreeBingo import settings
from .models import User, AccessToken, UserBalanceFilRecord
from .permissions import IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer, TokenSerializer, FillBalanceSerializer, ProfileSerializer, UserBalanceFillRecordSerializer
from bets.serializers import BetSerializer
from bets.models import Bet
from hashlib import sha256
from djmoney.money import Money


# Create your views here.


class UserCreationAPIView(generics.CreateAPIView):
    """
    Registration
    """

    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(token, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        password = make_password(serializer.data.get('password'))

        user = User.objects.create(
            email=serializer.data.get('email'),
            password=password,
            full_name=serializer.data.get('full_name'),
            phone_number=serializer.data.get('phone_number'),
            is_active=True,
        )

        token_instance = AccessToken.objects.create(user=user)

        return TokenSerializer(instance=token_instance).data


class RestAuthAPIView(generics.CreateAPIView):
    """
        Authentication
    """

    serializer_class = LoginSerializer

    def create(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        token = self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(token, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user: User = authenticate(email=serializer.data.get('email'), password=serializer.data.get('password'))

        if not user:
            raise exceptions.NotAuthenticated(detail='Email or password is incorrect')

        token_instance = AccessToken.objects.create(user=user)

        return TokenSerializer(instance=token_instance).data


class GetProfileAPIView(generics.RetrieveAPIView):
    """
        Get Profile by token
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user


class FillBalanceAPIView(generics.CreateAPIView):
    """
        Registration
    """

    serializer_class = FillBalanceSerializer
    permission_classes = (IsAuthenticated,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.record: Optional[UserBalanceFilRecord] = None

    def create(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        self.record = self.perform_create(serializer)
        sign = self.get_sign(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(self.send_payment_creation_request(sign), status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        amount = serializer.data.get('balance', 750.00)

        return UserBalanceFilRecord.objects.create(
            user=self.request.user,
            amount=amount,
            currency=643
        )

    def get_sign(self, serializer):
        amount = str(self.record.amount)
        currency = self.record.currency
        shop_id = settings.PIASTRIX_CONFIG.get('SHOP_ID')
        shop_order_id = self.record.id
        shop_secret = settings.PIASTRIX_CONFIG.get('SHOP_SECRET')

        sign_string = f'{amount}:{currency}:card_rub:{shop_id}:{shop_order_id}{shop_secret}'

        return sha256(sign_string.encode()).hexdigest()

    def send_payment_creation_request(self, sign):
        data = {
            'amount': self.record.amount,
            'currency': self.record.currency,
            'shop_id': settings.PIASTRIX_CONFIG.get('SHOP_ID'),
            'sign': sign,
            'shop_order_id': self.record.id,
            'payway': 'card_rub',
        }
        response = requests.post(settings.PIASTRIX_CONFIG.get('BASE_URL'), json=data)
        return response.json()

    def get_callback_urls(self):
        protocol = 'https' if self.request.is_secure() else 'http'
        site_url = f'{protocol}://{self.request.get_host()}'

        path = reverse('user:balance_fill_success')

        return {
            'success_url': f'{site_url}{path}',
            'failed_url': f'{site_url}{path}'
        }


class FillBalanceSuccessCallbackAPIView(views.APIView):
    swagger_schema = None

    def get(self, *args, **kwargs):
        record_id = self.request.query_params.get('shop_order_id', None)

        failure_path = reverse('user:balance_fill_failure')

        if not record_id:
            return HttpResponseRedirect(f'{failure_path}?reason=record_pk_absent')

        try:
            record = UserBalanceFilRecord.objects.get(id=record_id)
        except UserBalanceFilRecord.DoesNotExist:
            return HttpResponseRedirect(f'{failure_path}?reason=record_not_found')

        record.is_success = True
        record.user.balance = record.user.balance + Money(record.amount, 'RUB')
        record.user.save()

        return HttpResponseRedirect(f'{settings.FRONTEND_URL}/balance/fill/success/')


class FillBalanceFailureCallbackAPIView(views.APIView):
    swagger_schema = None

    def get(self, *args, **kwargs):
        return HttpResponseRedirect(f'{settings.FRONTEND_URL}/balance/fill/failure/')


class UserFillHistoryAPIView(generics.ListAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = UserBalanceFillRecordSerializer

    def get_queryset(self):
        return UserBalanceFilRecord.objects.filter(user=self.request.user)


class UserBetsHistoryApiView(generics.ListAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = BetSerializer

    def get_queryset(self):
        return Bet.objects.select_related('coefficient').filter(user=self.request.user)
