from testing.testcases import TestCase
from inbox.services import NotificationService
from notifications.models import Notification


class NotificationServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.wl = self.create_user('wl')
        self.wl_hsu = self.create_user('wl_hsu')
        self.wl_tweet = self.create_tweet(self.wl)

    def test_send_comment_notification(self):
        # do not dispatch notification if tweet user == comment user
        comment = self.create_comment(self.wl, self.wl_tweet)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(), 0)

        # dispatch notification if tweet user != comment user
        comment = self.create_comment(self.wl_hsu, self.wl_tweet)
        NotificationService.send_comment_notification(comment)
        self.assertEqual(Notification.objects.count(), 1)

    def test_send_like_notification(self):
        # do not dispatch notification if tweet user == like user
        like = self.create_like(self.wl, self.wl_tweet)
        NotificationService.send_like_notification(like)
        self.assertEqual(Notification.objects.count(), 0)

        # dispatch notification if tweet user != comment user
        like = self.create_comment(self.wl_hsu, self.wl_tweet)
        NotificationService.send_comment_notification(like)
        self.assertEqual(Notification.objects.count(), 1)