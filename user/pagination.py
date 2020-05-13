from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class TransactionPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_next_page_number(self):
        if not self.page.has_next():
            return None
        return self.page.next_page_number()

    def get_prev_page_number(self):
        if not self.page.has_previous():
            return None
        return self.page.previous_page_number()

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_page_number()),
            ('previous', self.get_prev_page_number()),
            ('results', data)
        ]))
