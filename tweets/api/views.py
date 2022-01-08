from rest_framework import viewsets
from newsfeeds.services import NewsFeedService
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerForDetail
)
from tweets.models import Tweet
from utils.decorators import required_params
from utils.paginations import EndlessPagination


class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin):
    """
    API endpoint that allows users to create, list tweets
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate
    pagination_class = EndlessPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        # <HOMEWORK 1> Use a query parameter with_all_comments to decide whether you need to bring all comments
        # <HOMEWORK 2> Use a query parameter with_preview_comments to decide whether to bring the first three comments
        serializer = TweetSerializerForDetail(
            self.get_object(),
            context={'request': request},
        )
        return Response(serializer.data)

    @required_params(params=['user_id'])
    def list(self, request, *args, **kwargs):
        # This query will be translated into
        # select * from twitter_tweets
        # where user_id = xxx
        # order by created_at desc
        # This SQL query will use the combined index of user and created_at
        # Mere user index is not enough
        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')
        tweets = self.paginate_queryset(tweets)
        serializer = TweetSerializer(
            tweets,
            context={'request': request},
            many=True,
        )
        # Generally speaking, json format response must use hash format by default
        # Instead of using the format of list (by convention)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Overload the create method, because you need to use the currently logged-in user as tweet.user by default
        """
        serializer = TweetSerializerForCreate(
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
        NewsFeedService.fanout_to_followers(tweet)
        serializer = TweetSerializer(tweet, context={'request': request})
        return Response(serializer.data, status=201)