from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Like(models.Model):
    # https://docs.djangoproject.com/en/3.1/ref/contrib/contenttypes/#generic-relations
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
    )
    # user liked content_object at created_at
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Using unique together here will also build an index of <user, content_type, object_id>.
        # This index can also have the function of querying which different objects a user likes
        # Therefore, if unique together is changed to <content_type, object_id, user>, there will be no such effect.
        unique_together = (('user', 'content_type', 'object_id'),)
        # The function of this index is to sort all likes of a content_object that is like by time
        index_together = (('content_type', 'object_id', 'created_at'),)

    def __str__(self):
        return '{} - {} liked {} {}'.format(
            self.created_at,
            self.user,
            self.content_type,
            self.object_id,
        )
