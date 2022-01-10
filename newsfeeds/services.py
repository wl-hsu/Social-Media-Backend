from newsfeeds.tasks import fanout_newsfeeds_task
from newsfeeds.models import NewsFeed
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_helper import RedisHelper


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        # The effect of this sentence is that the task parameter of creating a fanout in the message queue configured by
        # celery is tweet. Any worker process monitoring the message queue has the opportunity to get this task.
        # The code in fanout_newsfeeds_task will be executed in the worker process to implement an asynchronous task processing.
        # If the task needs to be processed for 10s, the 10s will be spent on the worker process,
        # not the Spend in the process of user tweeting. Therefore, the .delay operation will be executed immediately and
        # will end immediately without affecting the normal operation of the user.
        # (Because only a task is created here, the task information is placed in the message queue, and
        # this function is not actually executed) It should be noted that the parameters in delay must be values that
        # can be serialized by celery, because the worker process is an independent process, even on different machines,
        # there is no way to know what is the value in a certain memory space of the current web process.
        # So we can only pass tweet.id as a parameter, but not tweet. Because celery doesn't know how to serialize Tweet.
        fanout_newsfeeds_task.delay(tweet.id)

    @classmethod
    def get_cached_newsfeeds(cls, user_id):
        queryset = NewsFeed.objects.filter(user_id=user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key, queryset)

    @classmethod
    def push_newsfeed_to_cache(cls, newsfeed):
        queryset = NewsFeed.objects.filter(user_id=newsfeed.user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=newsfeed.user_id)
        RedisHelper.push_object(key, newsfeed, queryset)
