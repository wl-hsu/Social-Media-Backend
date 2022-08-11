from rest_framework.test import APIClient
from testing.testcases import TestCase
from gatekeeper.models import GateKeeper
from newsfeeds.models import NewsFeed, HBaseNewsFeed
from utils.paginations import EndlessPagination
from newsfeeds.services import NewsFeedService
from django.conf import settings


NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTests(TestCase):

    def setUp(self):
        super(NewsFeedApiTests, self).setUp()
        self.wl = self.create_user('wl')
        self.wl_client = APIClient()
        self.wl_client.force_authenticate(self.wl)

        self.wl_hsu = self.create_user('wl_hsu')
        self.wl_hsu_client = APIClient()
        self.wl_hsu_client.force_authenticate(self.wl_hsu)

        # create followings and followers for wl_hsu
        for i in range(2):
            follower = self.create_user('wl_hsu_follower{}'.format(i))
            self.create_friendship(from_user=follower, to_user=self.wl_hsu)
        for i in range(3):
            following = self.create_user('wl_hsu_following{}'.format(i))
            self.create_friendship(from_user=self.wl_hsu, to_user=following)

    def test_list(self):
        # Login required
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)
        # Can't use post
        response = self.wl_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)
        # Nothing at first
        response = self.wl_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)
        # user can see his/her own messages
        self.wl_client.post(POST_TWEETS_URL, {'content': 'Hello World'})
        response = self.wl_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['results']), 1)
        # 关After following, user can see other people's posts
        self.wl_client.post(FOLLOW_URL.format(self.wl_hsu.id))
        response = self.wl_hsu_client.post(POST_TWEETS_URL, {
            'content': 'Hello Twitter',
        })
        posted_tweet_id = response.data['id']
        response = self.wl_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['tweet']['id'], posted_tweet_id)

    def test_pagination(self):
        page_size = EndlessPagination.page_size
        followed_user = self.create_user('followed')
        newsfeeds = []
        for i in range(page_size * 2):
            tweet = self.create_tweet(followed_user)
            newsfeed = self.create_newsfeed(user=self.wl, tweet=tweet)
            newsfeeds.append(newsfeed)

        newsfeeds = newsfeeds[::-1]

        # pull the first page
        response = self.wl_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.data['has_next_page'], True)
        results = response.data['results']
        self.assertEqual(len(results), page_size)
        self.assertEqual(results[0]['created_at'], newsfeeds[0].created_at)
        self.assertEqual(results[1]['created_at'], newsfeeds[1].created_at)
        self.assertEqual(results[page_size - 1]['created_at'], newsfeeds[page_size - 1].created_at)

        # pull the second page
        response = self.wl_client.get(
            NEWSFEEDS_URL,
            {'created_at__lt': newsfeeds[page_size - 1].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        results = response.data['results']
        self.assertEqual(len(results), page_size)
        self.assertEqual(results[0]['created_at'], newsfeeds[page_size].created_at)
        self.assertEqual(results[1]['created_at'], newsfeeds[page_size + 1].created_at)
        self.assertEqual(
            results[page_size - 1]['created_at'],
            newsfeeds[2 * page_size - 1].created_at,
        )

        # pull latest newsfeeds
        response = self.wl_client.get(
            NEWSFEEDS_URL,
            {'created_at__gt': newsfeeds[0].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 0)

        tweet = self.create_tweet(followed_user)
        new_newsfeed = self.create_newsfeed(user=self.wl, tweet=tweet)

        response = self.wl_client.get(
            NEWSFEEDS_URL,
            {'created_at__gt': newsfeeds[0].created_at},
        )
        self.assertEqual(response.data['has_next_page'], False)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['created_at'], new_newsfeed.created_at)

    def test_user_cache(self):
        profile = self.wl_hsu.profile
        profile.nickname = 'wl_hsu_nickname'
        profile.save()

        self.assertEqual(self.wl.username, 'wl')
        self.create_newsfeed(self.wl_hsu, self.create_tweet(self.wl))
        self.create_newsfeed(self.wl_hsu, self.create_tweet(self.wl_hsu))

        response = self.wl_hsu_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'wl_hsu')
        # self.assertEqual(results[0]['tweet']['user']['nickname'], 'wl_hsu_nickname')
        self.assertEqual(results[1]['tweet']['user']['username'], 'wl')

        self.wl.username = 'wlnewname'
        self.wl.save()
        profile.nickname = 'tragos'
        profile.save()

        response = self.wl_hsu_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'wl_hsu')
        # self.assertEqual(results[0]['tweet']['user']['nickname'], 'tragos')
        self.assertEqual(results[1]['tweet']['user']['username'], 'wlnewname')

    def test_tweet_cache(self):
        tweet = self.create_tweet(self.wl, 'content1')
        self.create_newsfeed(self.wl_hsu, tweet)
        response = self.wl_hsu_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'wl')
        self.assertEqual(results[0]['tweet']['content'], 'content1')

        # update username
        self.wl.username = 'wlhsu'
        self.wl.save()
        response = self.wl_hsu_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['user']['username'], 'wlhsu')

        # update content
        tweet.content = 'content2'
        tweet.save()
        response = self.wl_hsu_client.get(NEWSFEEDS_URL)
        results = response.data['results']
        self.assertEqual(results[0]['tweet']['content'], 'content2')

    def _paginate_to_get_newsfeeds(self, client):
        # paginate until the end
        response = client.get(NEWSFEEDS_URL)
        results = response.data['results']
        while response.data['has_next_page']:
            created_at__lt = response.data['results'][-1]['created_at']
            response = client.get(NEWSFEEDS_URL, {'created_at__lt': created_at__lt})
            results.extend(response.data['results'])
        return results

    def test_redis_list_limit(self):
        list_limit = settings.REDIS_LIST_LENGTH_LIMIT
        page_size = 20
        users = [self.create_user('user{}'.format(i)) for i in range(5)]
        newsfeeds = []
        for i in range(list_limit + page_size):
            tweet = self.create_tweet(user=users[i % 5], content='feed{}'.format(i))
            feed = self.create_newsfeed(self.wl, tweet)
            newsfeeds.append(feed)
        newsfeeds = newsfeeds[::-1]

        # only cached list_limit objects
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(self.wl.id)
        self.assertEqual(len(cached_newsfeeds), list_limit)
        if GateKeeper.is_switch_on('switch_newsfeed_to_hbase'):
            count = len(HBaseNewsFeed.filter(prefix=(self.wl.id, None)))
        else:
            count = NewsFeed.objects.filter(user=self.wl).count()
        self.assertEqual(count, list_limit + page_size)

        results = self._paginate_to_get_newsfeeds(self.wl_client)
        self.assertEqual(len(results), list_limit + page_size)
        for i in range(list_limit + page_size):
            self.assertEqual(newsfeeds[i].created_at, results[i]['created_at'])

        # a followed user create a new tweet
        self.create_friendship(self.wl, self.wl_hsu)
        new_tweet = self.create_tweet(self.wl_hsu, 'a new tweet')
        NewsFeedService.fanout_to_followers(new_tweet)

        def _test_newsfeeds_after_new_feed_pushed():
            results = self._paginate_to_get_newsfeeds(self.wl_client)
            self.assertEqual(len(results), list_limit + page_size + 1)
            self.assertEqual(results[0]['tweet']['id'], new_tweet.id)
            for i in range(list_limit + page_size):
                self.assertEqual(newsfeeds[i].created_at, results[i + 1]['created_at'])

        _test_newsfeeds_after_new_feed_pushed()

        # cache expired
        self.clear_cache()
        _test_newsfeeds_after_new_feed_pushed()