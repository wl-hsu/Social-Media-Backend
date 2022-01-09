from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from likes.models import Like
from utils.time_helpers import utc_now
from tweets.constants import TweetPhotoStatus, TWEET_PHOTO_STATUS_CHOICES
from accounts.services import UserService


class Tweet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='who posts this tweet',
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at')

    def __str__(self):
        # Here is what will be displayed when you execute print(tweet instance)
        return f'{self.created_at} {self.user}: {self.content}'

    @property
    def hours_to_now(self):
        # datetime.now without time zone information,  need to add utc time zone information
        return (utc_now() - self.created_at).seconds // 3600

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')

    @property
    def cached_user(self):
        return UserService.get_user_through_cache(self.user_id)


class TweetPhoto(models.Model):
    # Under which Tweet the picture is
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)

    # Who uploaded this picture, although this information can be obtained from the tweet,
    # but repeated records in the Image can bring a lot of traversal in use, for example,
    # a person often uploads some illegal photos,
    # then this person uploads new The photos can be marked as key review objects.
    # Or when we need to block all photos uploaded by a certain user, we can quickly filter through this model
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    # Picture file
    file = models.FileField()
    order = models.IntegerField(default=0)

    # Picture status, used for review, etc.
    status = models.IntegerField(
        default=TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES,
    )

    # Soft delete mark. When a photo is deleted, it will first be marked as deleted,
    # and it will be deleted after a certain period of time.
    # The purpose of this is that if a true deletion is executed immediately when a tweet is deleted,
    # it usually takes a certain amount of time, which affects efficiency.
    # We can use asynchronous tasks to slowly do true deletions in the background.
    has_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('user', 'created_at'),
            ('has_deleted', 'created_at'),
            ('status', 'created_at'),
            ('tweet', 'order'),
        )

    def __str__(self):
        return f'{self.tweet_id}: {self.file}'