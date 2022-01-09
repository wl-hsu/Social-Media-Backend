from testing.testcases import TestCase
from datetime import timedelta
from utils.time_helpers import utc_now
from testing.testcases import TestCase
from tweets.constants import TweetPhotoStatus
from tweets.models import TweetPhoto


class TweetTests(TestCase):
    def setUp(self):
        self.clear_cache()
        self.wl = self.create_user('wl')
        self.tweet = self.create_tweet(self.wl, content='HOW DO YOU TURN THIS ON')

    def test_hours_to_now(self):
        self.tweet.created_at = utc_now() - timedelta(hours=10)
        self.tweet.save()
        self.assertEqual(self.tweet.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.wl, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.wl, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        wl_hsu = self.create_user('wl_hsu')
        self.create_like(wl_hsu, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)

    def test_create_photo(self):
        # The test can successfully create the data object of photo
        photo = TweetPhoto.objects.create(
            tweet=self.tweet,
            user=self.wl,
        )
        self.assertEqual(photo.user, self.wl)
        self.assertEqual(photo.status, TweetPhotoStatus.PENDING)
        self.assertEqual(self.tweet.tweetphoto_set.count(), 1)