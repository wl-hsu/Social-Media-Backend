from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetCreateSerializer
from tweets.models import Tweet


class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin):
    """
    API endpoint that allows users to create, list tweets
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetCreateSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        """
        Overload the list method, do not list all tweets, you must specify user_id as the filter condition
        """
        if 'user_id' not in request.query_params:
            return Response('missing user_id', status=400)

        # This query will be translated into
        # select * from twitter_tweets
        # where user_id = xxx
        # order by created_at desc
        # This SQL query will use the combined index of user and created_at
        # Mere user index is not enough
        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')
        serializer = TweetSerializer(tweets, many=True)
        # Generally speaking, json format response must use hash format by default
        # Instead of using the format of list (by convention)
        return Response({'tweets': serializer.data})

    def create(self, request, *args, **kwargs):
        """
        Overload the create method, because you need to use the currently logged-in user as tweet.user by default
        """
        serializer = TweetCreateSerializer(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)
        tweet = serializer.save()
        return Response(TweetSerializer(tweet).data, status=201)