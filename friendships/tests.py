from friendships.models import Friendship
from friendships.services import FriendshipService
from testing.testcases import TestCase


class FriendshipServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.wl = self.create_user('wl')
        self.wl_hsu = self.create_user('wl_hsu')

    def test_get_followings(self):
        user1 = self.create_user('user1')
        user2 = self.create_user('user2')
        for to_user in [user1, user2, self.wl_hsu]:
            Friendship.objects.create(from_user=self.wl, to_user=to_user)
        FriendshipService.invalidate_following_cache(self.wl.id)

        user_id_set = FriendshipService.get_following_user_id_set(self.wl.id)
        self.assertSetEqual(user_id_set, {user1.id, user2.id, self.wl_hsu.id})

        Friendship.objects.filter(from_user=self.wl, to_user=self.wl_hsu).delete()
        FriendshipService.invalidate_following_cache(self.wl.id)
        user_id_set = FriendshipService.get_following_user_id_set(self.wl.id)
        self.assertSetEqual(user_id_set, {user1.id, user2.id})