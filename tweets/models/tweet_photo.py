from .tweet import Tweet
from django.contrib.auth.models import User
from django.db import models
from tweets.constants import TweetPhotoStatus, TWEET_PHOTO_STATUS_CHOICES


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