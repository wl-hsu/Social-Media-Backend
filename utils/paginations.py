from dateutil import parser
from rest_framework.pagination import BasePagination
from rest_framework.response import Response
from django.conf import settings


class EndlessPagination(BasePagination):
    page_size = 20

    def __init__(self):
        super(EndlessPagination, self).__init__()
        self.has_next_page = False

    def to_html(self):
        pass

    def paginate_queryset(self, queryset, request, view=None):

        if 'created_at__gt' in request.query_params:
            # created_at__gt is used to load the latest content when pulling down to refresh
            # For the sake of simplicity, pull-down refresh does not do page turning mechanism,
            # and directly loads all updated data
            # Because if the data has not been updated for a long time,
            # it will not be updated by pull-down refresh, but the latest data will be reloaded
            created_at__gt = request.query_params['created_at__gt']
            queryset = queryset.filter(created_at__gt=created_at__gt)
            self.has_next_page = False
            return queryset.order_by('-created_at')

        if 'created_at__lt' in request.query_params:
            # created_at__lt is used to load the next page of data when scrolling up (page down) to
            # find the first page_size + 1 objects in the reverse order of created_at < created_at__lt objects.
            # For example, the current created_at list is [10, 9, 8, 7 .. 1] If created_at__lt=10 page_size = 2,
            # it should return [9, 8, 7]. The reason for returning one more object is to determine whether to
            # return the next page to reduce an empty load.
            created_at__lt = request.query_params['created_at__lt']
            queryset = queryset.filter(created_at__lt=created_at__lt)

        queryset = queryset.order_by('-created_at')[:self.page_size + 1]
        self.has_next_page = len(queryset) > self.page_size
        return queryset[:self.page_size]

    def get_paginated_response(self, data):
        return Response({
            'has_next_page': self.has_next_page,
            'results': data,
        })

    def paginate_ordered_list(self, reverse_ordered_list, request):
        if 'created_at__gt' in request.query_params:
            created_at__gt = parser.isoparse(request.query_params['created_at__gt'])
            objects = []
            for obj in reverse_ordered_list:
                if obj.created_at > created_at__gt:
                    objects.append(obj)
                else:
                    break
            self.has_next_page = False
            return objects

        index = 0
        if 'created_at__lt' in request.query_params:
            created_at__lt = parser.isoparse(request.query_params['created_at__lt'])
            for index, obj in enumerate(reverse_ordered_list):
                if obj.created_at < created_at__lt:
                    break
            else:
                # No objects are found that satisfy the condition, return an empty array
                # Note that this else corresponds to for, see python's for else syntax
                reverse_ordered_list = []
        self.has_next_page = len(reverse_ordered_list) > index + self.page_size
        return reverse_ordered_list[index: index + self.page_size]

    def paginate_cached_list(self, cached_list, request):
        paginated_list = self.paginate_ordered_list(cached_list, request)
        # If it is a page up, paginated_list contains all the latest data, return directly
        if 'created_at__gt' in request.query_params:
            return paginated_list
        # If there is still another page, it means that the data in the cached_list has not been fetched,
        # and it will return directly.
        if self.has_next_page:
            return paginated_list
        # If the length of the cached_list is less than the maximum limit,
        # it means that the cached_list already contains all the data
        if len(cached_list) < settings.REDIS_LIST_LENGTH_LIMIT:
            return paginated_list
        # If enter here, it means that there may be data in the database that is not loaded in the cache,
        # need to go directly to the database to query
        return None
