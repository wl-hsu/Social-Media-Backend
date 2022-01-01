from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
)


class CommentViewSet(viewsets.GenericViewSet):
    """
    Only implement the methods of list, create, update, destroy
    Does not implement the retrieve (query single comment) method, because there is no such requirement
    """
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()

    # POST /api/comments/ -> create
    # GET /api/comments/ -> list
    # POST /api/comments/1/ -> retrieve
    # DELETE /api/comments/1/ -> destroy
    # PATCH /api/comments/1/ -> partial_update
    # PUT /api/comments/1/ -> update

    def get_permissions(self):
        # Note that you need to use AllowAny() / IsAuthenticated() to instantiate the object
        # Instead of AllowAny / IsAuthenticated, this is just a class name
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }
        # Note that 'data=' must be added here to specify that the parameter is passed to data,
        # because the default first parameter is instance
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # The save method will trigger the create method in the serializer,
        # click into the specific implementation of save to see
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )