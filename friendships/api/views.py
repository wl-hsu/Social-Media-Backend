from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowingSerializer,
    FollowerSerializer,
    FriendshipSerializerForCreate,
)
from django.contrib.auth.models import User


class FriendshipViewSet(viewsets.GenericViewSet):
    # We hope that POST /api/friendship/1/follow is to follow the user with user_id=1
    # So here queryset needs to be User.objects.all()
    # If it is Friendship.objects.all, 404 Not Found will appear
    # Because the actions with detail=True will call get_object() first by default, which is
    # queryset.filter(pk=1) Query whether this object is
    serializer_class = FriendshipSerializerForCreate
    queryset = User.objects.all()

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        # GET /api/friendships/1/followers/
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        serializer = FollowerSerializer(friendships, many=True)
        return Response(
            {'followers': serializer.data},
            status=status.HTTP_200_OK,
        )

    # def list(self, request):
    #     return Response({'message': 'this is friendships home page'})

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        serializer = FollowingSerializer(friendships, many=True)
        return Response(
            {'followings': serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # Special judgments of repeated follow (for example, how many times do you follow the front end)
        # Silent processing, no error is reported, because this kind of repetitive operation will be more
        # due to network delays, and there is no need to treat it as an error
        if Friendship.objects.filter(from_user=request.user, to_user=pk).exists():
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
    def unfollow(self, request, pk):
        # Note that the type of pk is str, so type conversion is required
        if request.user.id == int(pk):
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)
        # https://docs.djangoproject.com/en/3.1/ref/models/querysets/#delete
        # The delete operation of Queryset returns two values, one is how much data is deleted,
        # the other is how much is deleted for each type
        # Why does the deletion of multiple types of data occur?
        # Because the cascade may be cascaded due to the foreign key setting
        # Delete, that is, for example, a certain attribute of A model is the foreign key of B model, and set
        # on_delete=models.CASCADE, then when some data of B is deleted, the association in A will also be deleted.
        # So CASCADE is very dangerous, we generally best not use it, but use on_delete=models.SET_NULL
        # Instead, this can at least avoid the domino effect caused by accidental deletion.
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=pk,
        ).delete()
        return Response({'success': True, 'deleted': deleted})