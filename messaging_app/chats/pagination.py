from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class MessagePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Return a custom paginated response that includes
        the total count of messages using page.paginator.count.
        """
        return Response({
            'count': self.page.paginator.count,       # ← uses page.paginator.count
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })
