from notifications.models import Notification
from testing.testcases import TestCase


COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'


class NotificationTests(TestCase):

    def setUp(self):
        self.wl, self.wl_client = self.create_user_and_client('wl')
        self.wl_hsu, self.wl_hsu_client = self.create_user_and_client('wl_hsu')
        self.wl_hsu_tweet = self.create_tweet(self.wl_hsu)

    def test_comment_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.wl_client.post(COMMENT_URL, {
            'tweet_id': self.wl_hsu_tweet.id,
            'content': 'a ha',
        })
        self.assertEqual(Notification.objects.count(), 1)

    def test_like_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.wl_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.wl_hsu_tweet.id,
        })
        self.assertEqual(Notification.objects.count(), 1)
