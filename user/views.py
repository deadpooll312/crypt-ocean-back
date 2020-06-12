import re
import smtplib
from typing import Optional
import requests
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, views, exceptions
from rest_framework.response import Response

from BefreeBingo import settings
from .constants import BONUS_TRANSACTION
from .mixins import BitchangeUtilsMixin
from .models import User, AccessToken, UserBalanceFilRecord, Transaction, PasswordRecoverToken, UserTraffic
from .pagination import TransactionPagination
from .permissions import IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer, TokenSerializer, FillBalanceSerializer, ProfileSerializer, UserBalanceFillRecordSerializer, TransactionSerializer, BalanceFillResponseSerializer, BalanceFillConfirmSerializer, UserUpdateSerializer, RecoverPasswordRequestSerializer, \
    ChangePasswordSerializer, UserTrafficSerializer
from bets.serializers import BetSerializer
from bets.models import Bet
from djmoney.money import Money
from .utils import get_client_ip, send_password_confirm_letter

# Create your views here.


@method_decorator(swagger_auto_schema(
    operation_summary='Регистрация',
    query_serializer=RegisterSerializer(),
    responses={
        201: TokenSerializer()
    }
), name='post')
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
        password = make_password(serializer.validated_data.get('password'))

        user = User.objects.create(
            email=serializer.validated_data.get('email'),
            password=password,
            full_name=serializer.validated_data.get('full_name'),
            phone_number=serializer.validated_data.get('phone_number'),
            is_active=True,
        )

        if serializer.validated_data.get('promo_code'):
            print(serializer.validated_data.get('promo_code'))
            user.related_referer = serializer.validated_data.get('promo_code')
            user.save()

        token_instance = AccessToken.objects.create(user=user)

        return TokenSerializer(instance=token_instance).data


@method_decorator(swagger_auto_schema(
    operation_summary='Авторизация',
    query_serializer=LoginSerializer(),
    responses={
        201: TokenSerializer()
    }
), name='post')
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


@method_decorator(swagger_auto_schema(
    operation_summary='Получение профиля по токену',
), name='get')
class GetProfileAPIView(generics.RetrieveAPIView):
    """
        Get Profile by token
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user


@method_decorator(swagger_auto_schema(
    operation_summary='Запрос на пополнение баланса',
    responses={
        201: BalanceFillResponseSerializer(),
    }
), name='post')
class FillBalanceAPIView(generics.CreateAPIView, BitchangeUtilsMixin):
    """
        Registration
    """

    serializer_class = FillBalanceSerializer
    permission_classes = (IsAuthenticated,)

    bit_change_url = settings.BITCHANGE_CONFIG.get('BASE_URL', 'https://api.bitchange.online/api/v1/create_order')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.record: Optional[UserBalanceFilRecord] = None

    def get_callback_urls(self):
        protocol = 'https' if self.request.is_secure() else 'http'
        site_url = f'{protocol}://{self.request.get_host()}'

        path = reverse('user:balance_fill_callback', kwargs={'record_id': self.record.id})

        return f'{site_url}{path}'

    def get_bitchange_response(self):
        data = {
            "invoice_type": 2,
            "amount": self.record.amount,
            "currency": "RUDT",
            "currency_receive": "RUDT",
            "order_id": self.record.id,
            "order_description": "Пополнение баланса на befree.bingo",
            # "return_url": self.get_callback_urls(),
            "ip": get_client_ip(self.request),
            "phone_number": re.sub(re.compile(r'\s', re.IGNORECASE), '', self.record.user.phone_number or ''),
            "email": self.record.user.email,
            "success_url": settings.FRONTEND_URL + '/success?record_token=' + str(self.record.token),
            "failed_url": settings.FRONTEND_URL + '/failure?record_token=' + str(self.record.token),
        }

        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/json'
        }
        headers.update(self.get_bitchange_auth_headers())
        response = requests.post(self.bit_change_url, json=data, headers=headers)
        return self.format_bitchange_response(response.json())

    def format_bitchange_response(self, response):
        if response.get('result', 'failed') != 'success':
            error_message = [
                f'Error Code: {response.get("error_code")}. Message: {response.get("error_message")}'
            ]

            if response.get('error_code', 1) == 200:
                validation_error: dict = response.get('validation', {})
                for key in validation_error.keys():
                    error_message.append(f'{key}: {", ".join(validation_error.get(key))}')

            raise exceptions.ValidationError({
                'bitchange': error_message
            })

        return response

    def create(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        self.record = self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(self.get_bitchange_response(), status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        amount = serializer.data.get('balance', '750.00')

        return UserBalanceFilRecord.objects.create(
            user=self.request.user,
            amount=amount,
            currency='RUDT'
        )


@method_decorator(swagger_auto_schema(
    operation_summary='Запрос на подтверждения пополнения баланса',
    responses={
        201: UserBalanceFillRecordSerializer(),
    },
), name='post')
class FillBalanceCallbackAPIView(generics.CreateAPIView, BitchangeUtilsMixin):
    serializer_class = BalanceFillConfirmSerializer
    permission_classes = (IsAuthenticated,)

    bitchange_url = 'https://api.bitchange.online/api/v1/order_details'
    pixel_url = 'https://install.partners/Services/pixel' \
                '?aid=839' \
                '&pid={partner_id}' \
                '&oid=839' \
                '&sid={site_id}' \
                '&geo={geo}' \
                '&hid={click_id}' \
                '&ip={ip}' \
                '&cost={cost}'

    def create(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        record = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(record, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        order_id = serializer.data.get('shop_order_id')
        try:
            record = UserBalanceFilRecord.objects.prefetch_related('user').get(id=serializer.data.get('shop_order_id'))
        except UserBalanceFilRecord.DoesNotExist:
            raise exceptions.ValidationError({'shop_order_id': ['Транзакция не найдена']})

        if record.is_finished:
            raise exceptions.ValidationError({'shop_order_id': ['Эта ссылка устарела']})

        if record.user != self.request.user:
            raise exceptions.PermissionDenied({'shop_order_id': ['Эта транзакция была совершена под другим аккаунтом']})

        record.is_finished = True

        self.check_payment(order_id, record)

        if serializer.data.get('status', 'failure') == 'success':
            self.add_balance_to_participants(record)

            self.send_traffic_percent(record)

            return UserBalanceFillRecordSerializer(instance=record).data

        record.is_success = False
        record.error_message = 'Bitchange payment failure'
        record.save(update_fields=['is_finished', 'is_success', 'error_message'])
        return UserBalanceFillRecordSerializer(instance=record).data

    def add_balance_to_participants(self, record: UserBalanceFilRecord):
        target_balance = Money(record.amount, 'RUB')

        record.is_success = True
        record.user.add_balance(target_balance)
        record.save(update_fields=['is_finished', 'is_success'])

        if record.user.related_referer:
            bonus_percent = target_balance / 100 * settings.REFERRAL_BONUS_PERCENT

            record.user.related_referer.add_balance(bonus_percent, BONUS_TRANSACTION, bonus_from=record.user)
            record.user.add_balance(bonus_percent, BONUS_TRANSACTION)

        return record

    def check_payment(self, order_id, record: UserBalanceFilRecord):
        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/json'
        }
        headers.update(self.get_bitchange_auth_headers())

        response = requests.post(self.bitchange_url, json={'order_id': order_id}, headers=headers)

        if response.status_code not in [200, 201]:
            raise exceptions.ValidationError({'shop_order_id': ['Сервера Bitchange не отвечают']})

        data = response.json()

        if data.get('order_status', None) is None:
            raise exceptions.ValidationError({'shop_order_id': ['Bitchange не вернула статус транзакции']})

        if data.get('order_status', None) in ['canceled', 'rejected']:
            record.is_success = False
            record.error_message = "Траназкция была отменена или отклонена"
            record.save()
            raise exceptions.ValidationError({'shop_order_id': ['Траназкция была отменена или отклонена']})

        if data.get('order_status', None) in ['expired']:
            raise exceptions.ValidationError({'shop_order_id': ['Ссылка устарела']})

        if data.get('order_status', None) in ['new', 'pending']:
            raise exceptions.ValidationError({'shop_order_id': ['Оплата ожидается! Попробуйте зайти на эту страницу позже!']})

    def get_exchange_rates(self):
        return requests.get('https://api.exchangeratesapi.io/latest?base=RUB&symbols=USD').json().get('rates')

    def get_geolocation_by_ip(self, ip):
        return requests.get(f'http://ip-api.com/json/{ip}').json().get('countryCode')

    def send_traffic_percent(self, record: UserBalanceFilRecord):
        ip = get_client_ip(self.request)

        traffic_instance: UserTraffic = UserTraffic.objects.filter(ip=ip).first()

        if traffic_instance:
            percent = Money(record.amount, 'RUB') / 100 * 30

            rates = self.get_exchange_rates()
            calculated_percent = Money(percent * rates['USD'], 'USD')

            target_url_with_params = self.pixel_url.format(
                partner_id=traffic_instance.partner_id,
                site_id=traffic_instance.site_id,
                geo=self.get_geolocation_by_ip(ip),
                click_id=traffic_instance.click_id,
                ip=ip,
                cost=calculated_percent
            )

            requests.get(target_url_with_params)

            traffic_instance.balance_filled = True
            traffic_instance.user = self.request.user
            traffic_instance.save()


# Deprecated
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

        return HttpResponseRedirect(f'{settings.FRONTEND_URL}/success/?record_signature={record.token}')


# Deprecated
class FillBalanceFailureCallbackAPIView(views.APIView):
    """
    (Deprecated)
    """
    swagger_schema = None

    def get(self, *args, **kwargs):
        return HttpResponseRedirect(f'{settings.FRONTEND_URL}/failure/')


class UserFillHistoryAPIView(generics.ListAPIView):
    swagger_schema = None

    permission_classes = (IsAuthenticated,)
    serializer_class = UserBalanceFillRecordSerializer

    def get_queryset(self):
        return UserBalanceFilRecord.objects.filter(user=self.request.user)


class UserBetsHistoryApiView(generics.ListAPIView):
    swagger_schema = None

    permission_classes = (IsAuthenticated,)
    serializer_class = BetSerializer

    def get_queryset(self):
        return Bet.objects.select_related('coefficient').filter(user=self.request.user)


class UserTransactionHistoryAPIView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = (IsAuthenticated,)

    pagination_class = TransactionPagination

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')


class UserUpdateAPIView(generics.UpdateAPIView):

    serializer_class = UserUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class RecoverPasswordAPIView(generics.CreateAPIView):

    serializer_class = RecoverPasswordRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'status': 'ok'}, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user = User.objects.get(email=serializer.data.get('email'))

        try:
            send_password_confirm_letter(self.request, user)
        except smtplib.SMTPServerDisconnected:
            raise exceptions.ValidationError({'smtp': ['Почтовый сервис не отвечает. Попробуйте позже.']})
        except ConnectionResetError:
            raise exceptions.ValidationError({'smtp': ['Почтовый сервис не отвечает. Попробуйте позже.']})


class CheckRecoverTokenAPIView(views.APIView):

    def post(self, *args, **kwargs):
        check_token = self.request.data.get('check_token', None)

        if not check_token:
            raise exceptions.ValidationError({
                'check_token': ['Поле `check_token` обязательное']
            })

        try:
            token_instance = PasswordRecoverToken.objects.get(token=check_token)
        except PasswordRecoverToken.DoesNotExist:
            raise exceptions.ValidationError({
                'check_token': ['Токен не валидный']
            })

        if token_instance.is_used:
            raise exceptions.ValidationError({
                'check_token': ['Токен устарел']
            })

        return Response({'status': 'ok'})


class ChangePasswordAPIView(generics.CreateAPIView):

    serializer_class = ChangePasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'status': 'ok'}, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        token_instance: PasswordRecoverToken = PasswordRecoverToken.objects.get(token=serializer.data.get('check_token'))
        token_instance.is_used = True
        token_instance.save(update_fields=['is_used'])

        token_instance.user.set_password(serializer.data.get('password'))
        token_instance.user.save()


class TrackUserTrafficAPIView(generics.CreateAPIView):

    serializer_class = UserTrafficSerializer

    def perform_create(self, serializer):
        traffic_instance: UserTraffic = UserTraffic.objects.filter(ip=get_client_ip(self.request)).first()

        if not traffic_instance:
            UserTraffic.objects.create(
                partner_id=serializer.validated_data.get('partner_id'),
                click_id=serializer.validated_data.get('click_id'),
                site_id=serializer.validated_data.get('site_id', None),
                ip=get_client_ip(self.request)
            )
        else:
            traffic_instance.partner_id = serializer.validated_data.get('partner_id')
            traffic_instance.click_id = serializer.validated_data.get('click_id')
            traffic_instance.site_id = serializer.validated_data.get('site_id', None)
            traffic_instance.save()
