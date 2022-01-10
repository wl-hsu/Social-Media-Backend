from celery import shared_task
from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from tweets.models import Tweet
from utils.time_constants import ONE_HOUR


@shared_task(time_limit=ONE_HOUR)
def fanout_newsfeeds_task(tweet_id):
    # import is written in it to avoid circular dependencies
    from newsfeeds.services import NewsFeedService

    # Wrong way
    # iF put database operations in the for loop, the efficiency will be very low
    # for follower in FriendshipService.get_followers(tweet.user):
    #     NewsFeed.objects.create(
    #         user=follower,
    #         tweet=tweet,
    #     )
    # Correct method: use bulk_create, which will combine the insert statement into one
    tweet = Tweet.objects.get(id=tweet_id)
    newsfeeds = [
        NewsFeed(user=follower, tweet=tweet)
        for follower in FriendshipService.get_followers(tweet.user)
    ]
    newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
    NewsFeed.objects.bulk_create(newsfeeds)

    # bulk create will not trigger the post_save signal, so you need to manually push it to the cache
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)