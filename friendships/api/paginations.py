from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class FriendshipPagination(PageNumberPagination):
    # The default page size, that is, when the page is not in the url parameter
    page_size = 20
    # The default page_size_query_param is None which means the client is not allowed to specify the size of each page
    # If this configuration is added, it means that the client can specify a specific size for different scenarios through size=10
    # For example, the mobile terminal and the web terminal access the same API but the required size is different.
    page_size_query_param = 'size'
    # what is the maximum page_size that the client is allowed to specify
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response({
            'total_results': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'has_next_page': self.page.has_next(),
            'results': data,
        })