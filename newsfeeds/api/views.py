from rest_framework import viewsets, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsFeedSerializer


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Custom queryset, because newsfeed viewing is authorized
        # can only see the newsfeed of user=currently logged in user
        # It can also be self.request.user.newsfeed_set.all()
        # But generally it is better to write in the way of NewsFeed.objects.filter, which is more clear and intuitive
        return NewsFeed.objects.filter(user=self.request.user)

    def list(self, request):
        serializer = NewsFeedSerializer(
            self.get_queryset(),
            context={'request': request},
            many=True,
        )
        return Response({
            'newsfeeds': serializer.data,
        }, status=status.HTTP_200_OK)