from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase


FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):

    def setUp(self):
        # self.anonymous_client = APIClient()

        self.wl = self.create_user('wl')
        self.wl_client = APIClient()
        self.wl_client.force_authenticate(self.wl)

        self.wl_hsu = self.create_user('wl_hsu')
        self.wl_hsu_client = APIClient()
        self.wl_hsu_client.force_authenticate(self.wl_hsu)

        # create followings and followers for wl_hsu
        for i in range(2):
            follower = self.create_user('wl_hsu_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.wl_hsu)
        for i in range(3):
            following = self.create_user('wl_hsu_following{}'.format(i))
            Friendship.objects.create(from_user=self.wl_hsu, to_user=following)

    def test_follow(self):
        url = FOLLOW_URL.format(self.wl.id)

        # need to log in to follow others
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # Use get to follow
        response = self.wl_hsu_client.get(url)
        self.assertEqual(response.status_code, 405)
        # Can't follow self
        response = self.wl_client.post(url)
        self.assertEqual(response.status_code, 400)
        # follow succeed
        response = self.wl_hsu_client.post(url)
        self.assertEqual(response.status_code, 201)
        # ignore duplicate follow
        response = self.wl_hsu_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['duplicate'], True)
        # Reverse following creates new data
        count = Friendship.objects.count()
        response = self.wl_client.post(FOLLOW_URL.format(self.wl_hsu.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.wl.id)

        # Need to log in to unfollow others
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # Can't use get to unfollow others
        response = self.wl_hsu_client.get(url)
        self.assertEqual(response.status_code, 405)
        # Can't use unfollow elf
        response = self.wl_client.post(url)
        self.assertEqual(response.status_code, 400)
        # unfollow succeed
        Friendship.objects.create(from_user=self.wl_hsu, to_user=self.wl)
        count = Friendship.objects.count()
        response = self.wl_hsu_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)
        # ignore unfollow if haven't followed
        count = Friendship.objects.count()
        response = self.wl_hsu_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.wl_hsu.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)
        # Make sure to reverse chronological order
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'wl_hsu_following2',
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'wl_hsu_following1',
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'wl_hsu_following0',
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.wl_hsu.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)
        # Make sure to reverse chronological order
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'wl_hsu_follower1',
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'wl_hsu_follower0',
        )