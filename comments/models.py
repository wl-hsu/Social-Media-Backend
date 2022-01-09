from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from likes.models import Like
from tweets.models import Tweet
from accounts.services import UserService


class Comment(models.Model):
    """
    In this version, first implement a relatively simple comment
    Comments only comment on a certain Tweet, you cannot comment on other people’s comments
    """
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    tweet = models.ForeignKey(Tweet, null=True, on_delete=models.SET_NULL)
    content = models.TextField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # There is a need to sort all comments under a certain tweet
        index_together = (('tweet', 'created_at'),)

    def __str__(self):
        return '{} - {} says {} at tweet {}'.format(
            self.created_at,
            self.user,
            self.content,
            self.tweet_id,
        )

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=self.id,
        ).order_by('-created_at')

    @property
    def cached_user(self):
        return UserService.get_user_through_cache(self.user_id)