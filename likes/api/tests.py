from testing.testcases import TestCase


LIKE_BASE_URL = '/api/likes/'


class LikeApiTests(TestCase):

    def setUp(self):
        self.wl, self.wl_client = self.create_user_and_client('wl')
        self.wl_hsu, self.wl_hsu_client = self.create_user_and_client('wl_hsu')

    def test_tweet_likes(self):
        tweet = self.create_tweet(self.wl)
        data = {'content_type': 'tweet', 'object_id': tweet.id}

        # anonymous is not allowed
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        # get is not allowed
        response = self.wl_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        # post success
        response = self.wl_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweet.like_set.count(), 1)

        # duplicate likes
        self.wl_client.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 1)
        self.wl_hsu_client.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 2)

    def test_comment_likes(self):
        tweet = self.create_tweet(self.wl)
        comment = self.create_comment(self.wl_hsu, tweet)
        data = {'content_type': 'comment', 'object_id': comment.id}

        # anonymous is not allowed
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        # get is not allowed
        response = self.wl_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        # wrong content_type
        response = self.wl_client.post(LIKE_BASE_URL, {
            'content_type': 'coment',
            'object_id': comment.id,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content_type' in response.data['errors'], True)

        # wrong object_id
        response = self.wl_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': -1,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('object_id' in response.data['errors'], True)

        # post success
        response = self.wl_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)

        # duplicate likes
        response = self.wl_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)
        self.wl_hsu_client.post(LIKE_BASE_URL, data)
        self.assertEqual(comment.like_set.count(), 2)