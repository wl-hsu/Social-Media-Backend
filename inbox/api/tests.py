from notifications.models import Notification
from testing.testcases import TestCase


COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'
NOTIFICATION_URL = '/api/notifications/'


class NotificationTests(TestCase):

    def setUp(self):
        super(NotificationTests, self).setUp()
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


class NotificationApiTests(TestCase):

    def setUp(self):
        self.wl, self.wl_client = self.create_user_and_client('wl')
        self.wl_hsu, self.wl_hsu_client = self.create_user_and_client('wl_hsu')
        self.wl_tweet = self.create_tweet(self.wl)

    def test_unread_count(self):
        self.wl_hsu_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.wl_tweet.id,
        })

        url = '/api/notifications/unread-count/'
        response = self.wl_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 1)

        comment = self.create_comment(self.wl, self.wl_tweet)
        self.wl_hsu_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        response = self.wl_client.get(url)
        self.assertEqual(response.data['unread_count'], 2)

    def test_mark_all_as_read(self):
        self.wl_hsu_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.wl_tweet.id,
        })
        comment = self.create_comment(self.wl, self.wl_tweet)
        self.wl_hsu_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        unread_url = '/api/notifications/unread-count/'
        response = self.wl_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        mark_url = '/api/notifications/mark-all-as-read/'
        response = self.wl_client.get(mark_url)
        self.assertEqual(response.status_code, 405)
        response = self.wl_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 2)
        response = self.wl_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 0)

    def test_list(self):
        self.wl_hsu_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.wl_tweet.id,
        })
        comment = self.create_comment(self.wl, self.wl_tweet)
        self.wl_hsu_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        # Anonymous users cannot access the api
        response = self.anonymous_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 403)
        # wl_hsu can't see any notifications
        response = self.wl_hsu_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        # wl see two notifications
        response = self.wl_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        # see an unread after marking
        notification = self.wl.notifications.first()
        notification.unread = False
        notification.save()
        response = self.wl_client.get(NOTIFICATION_URL)
        self.assertEqual(response.data['count'], 2)
        response = self.wl_client.get(NOTIFICATION_URL, {'unread': True})
        self.assertEqual(response.data['count'], 1)
        response = self.wl_client.get(NOTIFICATION_URL, {'unread': False})
        self.assertEqual(response.data['count'], 1)

    def test_update(self):
        self.wl_hsu_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.wl_tweet.id,
        })
        comment = self.create_comment(self.wl, self.wl_tweet)
        self.wl_hsu_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        notification = self.wl.notifications.first()

        url = '/api/notifications/{}/'.format(notification.id)
        # post doesn’t work, need to use put
        response = self.wl_hsu_client.post(url, {'unread': False})
        self.assertEqual(response.status_code, 405)
        # The notification status cannot be changed by others
        response = self.anonymous_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 403)
        # Because queryset is based on the currently logged in user, it will return 404 instead of 403
        response = self.wl_hsu_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 404)
        # Mark as read successfully
        response = self.wl_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 200)
        unread_url = '/api/notifications/unread-count/'
        response = self.wl_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 1)

        # Mark as unread again
        response = self.wl_client.put(url, {'unread': True})
        response = self.wl_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)
        # Must bring unread
        response = self.wl_client.put(url, {'verb': 'newverb'})
        self.assertEqual(response.status_code, 400)
        # No other information can be modified
        response = self.wl_client.put(url, {'verb': 'newverb', 'unread': False})
        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db()
        self.assertNotEqual(notification.verb, 'newverb')
