from typing import Optional

import requests
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from rest_framework import generics, status, views, exceptions
from rest_framework.response import Response

from CryptoOcean import settings
from .models import User, AccessToken, UserBalanceFilRecord
from .permissions import IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer, TokenSerializer, FillBalanceSerializer, ProfileSerializer
from hashlib import sha256


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
        password = make_password(serializer.data.get('password_confirm'))

        user = User.objects.create(
            email=serializer.data.get('email'),
            password=password,
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

        sign_string = f'{amount}:{currency}:{shop_id}:{shop_order_id}{shop_secret}'

        return sha256(sign_string.encode()).hexdigest()

    def send_payment_creation_request(self, sign):
        return {
            'url': settings.PIASTRIX_CONFIG.get('BASE_URL'),
            'data': {
                'amount': self.record.amount,
                'currency': self.record.currency,
                'shop_id': settings.PIASTRIX_CONFIG.get('SHOP_ID'),
                'sign': sign,
                'shop_order_id': self.record.id,
            }
        }
