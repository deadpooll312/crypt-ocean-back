import datetime
import hashlib
import hmac

import requests
from djmoney.money import Money

from BefreeBingo import settings
from user.models import UserBalanceFilRecord, UserTraffic, TrafficPercentPaymentLog
from user.utils import get_client_ip
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie


class BitchangeUtilsMixin:
    shop_id = settings.BITCHANGE_CONFIG.get('SHOP_ID', 'BlqWarhVLHmqA8DdPoZNK00xebYNDf')
    shop_secret = settings.BITCHANGE_CONFIG.get('SHOP_SECRET', 'KSvP4AwZG5tYWf1wWuw0meL3QAdJOp')

    def get_bitchange_auth_headers(self):
        nonce = datetime.datetime.now().microsecond

        sign_str = f'{nonce}|{self.shop_id}|{self.shop_secret}'
        sign = hmac.new(self.shop_secret.encode(), sign_str.encode(), hashlib.sha256).hexdigest()

        return {
            'C-Request-Nonce': f'{nonce}',
            'C-Request-Signature': sign,
            'C-Shop-Id': self.shop_id,
        }


class TrafficMixin:
    pixel_url = 'https://install.partners/Services/pixel' \
                '?aid=839' \
                '&pid={partner_id}' \
                '&oid=839' \
                '&sid={site_id}' \
                '&geo={geo}' \
                '&hid={click_id}' \
                '&ip={ip}' \
                '&cost={cost}'

    cityads_url = 'http://cityads.ru/service/postback/' \
                  '?order_id={order_id}' \
                  '&click_id={click_id}' \
                  '&commission={cost}' \
                  '&currency=USD'

    def get_percent_method_map(self):
        return {
            'mkt': self.mkt_percent,
            'cityads': self.city_ads_percent
        }

    def mkt_percent(self, record: UserBalanceFilRecord, traffic_instance: UserTraffic):
        ip = get_client_ip(self.request)
        percent = Money(record.amount, 'RUB') / 100 * 30

        calculated_percent = self.exchange_money(percent)

        target_url_with_params = self.pixel_url.format(
            partner_id=traffic_instance.partner_id,
            site_id=traffic_instance.site_id,
            geo=self.get_geolocation_by_ip(ip),
            click_id=traffic_instance.click_id,
            ip=ip,
            cost=calculated_percent
        )

        print("===================== URL ====================")
        print(target_url_with_params)
        print("===================== URL ====================")

        requests.get(target_url_with_params)

        traffic_instance.balance_filled = True
        traffic_instance.user = self.request.user
        traffic_instance.save(update_fields=['balance_filled', 'user'])

        self.log_traffic_percent(
            traffic_instance,
            Money(calculated_percent, 'USD'),
            target_url_with_params
        )

    def city_ads_percent(self, record: UserBalanceFilRecord, traffic_instance: UserTraffic):
        percent = Money(record.amount, 'RUB') / 100 * 30

        calculated_percent = self.exchange_money(percent)

        target_url_with_params = self.cityads_url.format(
            order_id=record.token,
            click_id=traffic_instance.click_id,
            cost=calculated_percent,
        )

        print("===================== URL ====================")
        print(target_url_with_params)
        print("===================== URL ====================")

        requests.get(target_url_with_params)

        traffic_instance.balance_filled = True
        traffic_instance.user = self.request.user
        traffic_instance.save()

        self.log_traffic_percent(
            traffic_instance,
            Money(calculated_percent, 'USD'),
            target_url_with_params
        )

    def log_traffic_percent(self, traffic_instance, cost, link):
        TrafficPercentPaymentLog.objects.create(
            traffic=traffic_instance,
            cost=cost,
            link=link,
            traffic_info='''
                                <span>
                                pid = {partner_id},<br/>
                                clickId = {click_id},<br/>
                                subid = {site_id},<br/>
                                source = {src},<br/>
                                ip = {ip}<br />
                                </span>
                                '''.format(
                partner_id=traffic_instance.partner_id,
                click_id=traffic_instance.click_id,
                site_id=traffic_instance.site_id,
                src=traffic_instance.get_source_display(),
                ip=traffic_instance.ip
            )
        )

    def get_exchange_rates(self):
        return requests.get('https://api.exchangeratesapi.io/latest?base=RUB&symbols=USD').json().get('rates')

    def get_geolocation_by_ip(self, ip):
        return requests.get(f'http://ip-api.com/json/{ip}').json().get('countryCode')

    def exchange_money(self, amount: Money):
        rates = self.get_exchange_rates()
        print("===================== RATES ====================")
        print(rates)
        print(amount)
        print("===================== RATES ====================")
        return Money(float(amount.amount) * rates['USD'], 'USD').amount


class EnsureCsrfCookieMixin:
    """
    Ensures that the CSRF cookie will be passed to the client.
    NOTE:
        This should be the left-most mixin of a view.
    """

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(EnsureCsrfCookieMixin, self).dispatch(*args, **kwargs)
