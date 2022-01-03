from testing.testcases import TestCase


class CommentModelTests(TestCase):

    def test_comment(self):
        self.assertNotEqual(self.comment.__str__(), None)

    def setUp(self):
        self.wl = self.create_user('wl')
        self.tweet = self.create_tweet(self.wl)
        self.comment = self.create_comment(self.wl, self.tweet)

    def test_like_set(self):
        self.create_like(self.wl, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.create_like(self.wl, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        wl_hsu = self.create_user('wl_hsu')
        self.create_like(wl_hsu, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)
