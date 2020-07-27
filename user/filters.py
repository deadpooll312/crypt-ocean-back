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
    created_at = django_filters.CharFilter(field_name='created_at', lookup_expr='icontains')

    class Meta:
        model = UserClickTracker
        fields = [
            'area',
            'created_at'
        ]
