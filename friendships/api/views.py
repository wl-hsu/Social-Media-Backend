from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from friendships.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FriendshipSerializerForCreate,
)
from friendships.models import HBaseFollowing, HBaseFollower, Friendship
from friendships.services import FriendshipService
from gatekeeper.models import GateKeeper
from ratelimit.decorators import ratelimit
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from utils.paginations import EndlessPagination


class FriendshipViewSet(viewsets.GenericViewSet):
    # We hope that POST /api/friendship/1/follow is to follow the user with user_id=1
    # So here queryset needs to be User.objects.all()
    # If it is Friendship.objects.all, 404 Not Found will appear
    # Because the actions with detail=True will call get_object() first by default, which is
    # queryset.filter(pk=1) Query whether this object is
    queryset = User.objects.all()
    # Generally, the pagination rules required by different views must be different,
    # so they generally need to be customized
    pagination_class = EndlessPagination

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='GET', block=True))
    def followers(self, request, pk):
        if GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            page = self.paginator.paginate_hbase(HBaseFollower, (pk,), request)
        else:
            friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
            page = self.paginate_queryset(friendships)

        serializer = FollowerSerializer(page, many=True, context={'request': request})
        return self.paginator.get_paginated_response(serializer.data)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='GET', block=True))
    def followings(self, request, pk):
        if GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            page = self.paginator.paginate_hbase(HBaseFollowing, (pk,), request)
        else:
            friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
            page = self.paginate_queryset(friendships)

        serializer = FollowingSerializer(page, many=True, context={'request': request})
        return self.paginator.get_paginated_response(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def follow(self, request, pk):
        # Special judgments of repeated follow (for example, how many times do you follow the front end)
        # Silent processing, no error is reported, because this kind of repetitive operation will be more
        # due to network delays, and there is no need to treat it as an error
        if FriendshipService.has_followed(request.user.id, int(pk)):
            return Response({
                'success': True,
                'duplicate': True,
            }, status=status.HTTP_201_CREATED)
        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'success': True}, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def unfollow(self, request, pk):
        # Note that the type of pk is str, so type conversion is required
        if request.user.id == int(pk):
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)
        deleted = FriendshipService.unfollow(request.user.id, int(pk))
        return Response({'success': True, 'deleted': deleted})