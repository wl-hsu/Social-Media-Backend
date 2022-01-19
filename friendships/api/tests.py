from friendships.services import FriendshipService
from rest_framework.test import APIClient
from testing.testcases import TestCase
from utils.paginations import EndlessPagination


FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):

    def setUp(self):
        super(FriendshipApiTests, self).setUp()
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

    def test_follow(self):
        url = FOLLOW_URL.format(self.wl.id)

        # Login required to follow others
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # use get to follow
        response = self.wl_hsu_client.get(url)
        self.assertEqual(response.status_code, 405)
        # can't follow self
        response = self.wl_client.post(url)
        self.assertEqual(response.status_code, 400)
        # follow success
        response = self.wl_hsu_client.post(url)
        self.assertEqual(response.status_code, 201)
        # Repeat follow silently successfully
        response = self.wl_hsu_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['duplicate'], True)
        # Reverse following creates new data
        before_count = FriendshipService.get_following_count(self.wl.id)
        response = self.wl_client.post(FOLLOW_URL.format(self.wl_hsu.id))
        self.assertEqual(response.status_code, 201)
        after_count = FriendshipService.get_following_count(self.wl.id)
        self.assertEqual(after_count, before_count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.wl.id)

        # Login required to unfollow others
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # Can't use get to unfollow others
        response = self.wl_hsu_client.get(url)
        self.assertEqual(response.status_code, 405)
        # Can't unfollow self
        response = self.wl_client.post(url)
        self.assertEqual(response.status_code, 400)
        # unfollow success
        self.create_friendship(from_user=self.wl_hsu, to_user=self.wl)
        before_count = FriendshipService.get_following_count(self.wl_hsu.id)
        response = self.wl_hsu_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        after_count = FriendshipService.get_following_count(self.wl_hsu.id)
        self.assertEqual(after_count, before_count - 1)
        # Unfollow silent processing without follow
        before_count = FriendshipService.get_following_count(self.wl_hsu.id)
        response = self.wl_hsu_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        after_count = FriendshipService.get_following_count(self.wl_hsu.id)
        self.assertEqual(before_count, after_count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.wl_hsu.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)
        # Make sure to go in reverse chronological order
        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        ts2 = response.data['results'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['results'][0]['user']['username'],
            'wl_hsu_following2',
        )
        self.assertEqual(
            response.data['results'][1]['user']['username'],
            'wl_hsu_following1',
        )
        self.assertEqual(
            response.data['results'][2]['user']['username'],
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
        self.assertEqual(len(response.data['results']), 2)
        # Make sure to go in reverse chronological order
        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['results'][0]['user']['username'],
            'wl_hsu_follower1',
        )
        self.assertEqual(
            response.data['results'][1]['user']['username'],
            'wl_hsu_follower0',
        )

    def test_followers_pagination(self):
        page_size = EndlessPagination.page_size
        friendships = []
        for i in range(page_size * 2):
            follower = self.create_user('wl_follower{}'.format(i))
            friendship = self.create_friendship(from_user=follower, to_user=self.wl)
            friendships.append(friendship)
            if follower.id % 2 == 0:
                self.create_friendship(from_user=self.wl_hsu, to_user=follower)

        url = FOLLOWERS_URL.format(self.wl.id)
        self._paginate_until_the_end(url, 2, friendships)

        # anonymous hasn't followed any users
        response = self.anonymous_client.get(url)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # wl_hsu has followed users with even id
        response = self.wl_hsu_client.get(url)
        for result in response.data['results']:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)

    def test_followings_pagination(self):
        page_size = EndlessPagination.page_size
        friendships = []
        for i in range(page_size * 2):
            following = self.create_user('wl_following{}'.format(i))
            friendship = self.create_friendship(from_user=self.wl, to_user=following)
            friendships.append(friendship)
            if following.id % 2 == 0:
                self.create_friendship(from_user=self.wl_hsu, to_user=following)

        url = FOLLOWINGS_URL.format(self.wl.id)
        self._paginate_until_the_end(url, 2, friendships)

        # anonymous hasn't followed any users
        response = self.anonymous_client.get(url)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # wl_hsu has followed users with even id
        response = self.wl_hsu_client.get(url)
        for result in response.data['results']:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)

        # wl has followed all his following users
        response = self.wl_client.get(url)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], True)

        # test pull new friendships
        last_created_at = friendships[-1].created_at
        response = self.wl_client.get(url, {'created_at__gt': last_created_at})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        new_friends = [self.create_user('big_v{}'.format(i)) for i in range(3)]
        new_friendships = []
        for friend in new_friends:
            new_friendships.append(self.create_friendship(from_user=self.wl, to_user=friend))
        response = self.wl_client.get(url, {'created_at__gt': last_created_at})
        self.assertEqual(len(response.data['results']), 3)
        for result, friendship in zip(response.data['results'], reversed(new_friendships)):
            self.assertEqual(result['created_at'], friendship.created_at)

    def _paginate_until_the_end(self, url, expect_pages, friendships):
        results, pages = [], 0
        response = self.anonymous_client.get(url)
        results.extend(response.data['results'])
        pages += 1
        while response.data['has_next_page']:
            self.assertEqual(response.status_code, 200)
            last_item = response.data['results'][-1]
            response = self.anonymous_client.get(url, {
                'created_at__lt': last_item['created_at'],
            })
            results.extend(response.data['results'])
            pages += 1

        self.assertEqual(len(results), len(friendships))
        self.assertEqual(pages, expect_pages)
        # friendship is in ascending order, results is in descending order
        for result, friendship in zip(results, friendships[::-1]):
            self.assertEqual(result['created_at'], friendship.created_at)