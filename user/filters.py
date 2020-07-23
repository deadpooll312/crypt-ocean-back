import datetime

import django_filters
import pytz
from django.conf import settings
from django.db.models import Q

from user.models import UserTraffic, UserClickTracker


class UserTrafficFilter(django_filters.FilterSet):
    created_at = django_filters.CharFilter(field_name='created_at', lookup_expr='icontains')
    updated_at = django_filters.CharFilter(field_name='updated_at', lookup_expr='icontains')

    class Meta:
        model = UserTraffic
        fields = [
            'source',
            'balance_filled',
            'created_at',
            'updated_at'
        ]


class UserClickFilter(django_filters.FilterSet):
    created_at = django_filters.DateTimeFilter(field_name='created_at')
    # created_at = django_filters.CharFilter(field_name='created_at', method='filter_created_at')

    class Meta:
        model = UserClickTracker
        fields = [
            'area',
            'created_at'
        ]

    def filter_created_at(self, queryset, name, value):
        # for obj in queryset:
        #     print(obj.created_at)
        #
        value = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M')
        print('value => ', value)
        print('value => ', value.tzinfo)

        tz_string = datetime.datetime.now(datetime.timezone.utc).astimezone().tzname()
        print('tz_string= > ', tz_string)
        #
        # print('value => ', value)
        # print('timezone => ', timezone.now())
        #
        # new_value = timezone.datetime.strftime(value, '%Y-%m-%d %H:%M')

        moscow_tz = pytz.timezone(settings.TIME_ZONE)
        moscow = moscow_tz.localize(value)

        print('moscow => ', moscow)
        print('moscow => ', moscow.date())
        print('moscow => ', moscow.time())
        print('moscow => ', moscow.tzinfo)
        print('moscow => ', moscow.strftime('%Y-%m-%d %H:%M'))
        print('moscow => ', moscow.utcoffset())
        print('moscow => ', moscow.utcoffset().days)
        print('moscow => ', moscow.dst())

        # local_dt = timezone.localtime(moscow, '%Y-%m-%d %H:%M')
        # print('local_dt =>', local_dt)
        #
        # print('local_dt => ', local_dt)
        return queryset.filter(
            Q(created_at__icontains=moscow),
            # Q(created_at__icontains=time)
        )
