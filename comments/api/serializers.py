from accounts.api.serializers import UserSerializerForComments
from comments.models import Comment
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializerForComments()

    class Meta:
        model = Comment
        fields = ('id', 'tweet_id', 'user', 'content', 'created_at', 'updated_at',)


class CommentSerializerForCreate(serializers.ModelSerializer):
    # These two items must be added manually
    # Because the default ModelSerializer will only automatically include user and tweet instead of user_id and tweet_id
    tweet_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ('content', 'tweet_id', 'user_id')

    def validate(self, data):
        tweet_id = data['tweet_id']
        if not Tweet.objects.filter(id=tweet_id).exists():
            raise ValidationError({'message': 'tweet does not exist'})
        # Must return validated data
        # That is, input data that has been processed (of course,
        # it can also be processed without processing) after verification
        return data

    def create(self, validated_data):
        return Comment.objects.create(
            user_id=validated_data['user_id'],
            tweet_id=validated_data['tweet_id'],
            content=validated_data['content'],
        )