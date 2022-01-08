from rest_framework.test import APIClient
from comments.models import Comment
from django.utils import timezone
from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'
TWEET_LIST_API = '/api/tweets/'
TWEET_DETAIL_API = '/api/tweets/{}/'
NEWSFEED_LIST_API = '/api/newsfeeds/'


class CommentApiTests(TestCase):

    def setUp(self):
        self.wl = self.create_user('wl')
        self.wl_client = APIClient()
        self.wl_client.force_authenticate(self.wl)
        self.wl_hsu = self.create_user('wl_hsu')
        self.wl_hsu_client = APIClient()
        self.wl_hsu_client.force_authenticate(self.wl_hsu)

        self.tweet = self.create_tweet(self.wl)

    def test_create(self):
        # Anonymous cannot be created
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # need to bring some parameters
        response = self.wl_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # Only tweet_id will not work
        response = self.wl_client.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)

        # Only with content can not work
        response = self.wl_client.post(COMMENT_URL, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        # content is too long to work
        response = self.wl_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1' * 141,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        # Both tweet_id and content should be included
        response = self.wl_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.wl.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1')

    def test_destroy(self):
        comment = self.create_comment(self.wl, self.tweet)
        url = '{}{}/'.format(COMMENT_URL, comment.id)

        # Anonymous cannot delete comments
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # it can not be deleted if you are not the owner.
        response = self.wl_hsu_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # it can be deleted if you are the owner.
        count = Comment.objects.count()
        response = self.wl_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_update(self):
        comment = self.create_comment(self.wl, self.tweet, 'original')
        another_tweet = self.create_tweet(self.wl_hsu)
        url = '{}{}/'.format(COMMENT_URL, comment.id)

        # In the case of using put
        # Anonymous cannot update
        response = self.anonymous_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        # Cannot update if you are not the owner
        response = self.wl_hsu_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, 'new')
        # Cannot update the content other than content, silently process, only update the content
        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.wl_client.put(url, {
            'content': 'new',
            'user_id': self.wl_hsu.id,
            'tweet_id': another_tweet.id,
            'created_at': now,
        })
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.wl)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.created_at, now)
        self.assertNotEqual(comment.updated_at, before_updated_at)

    def test_list(self):
        # Must bring tweet_id
        response = self.anonymous_client.get(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # can visit with tweet_id
        # No comments at the beginning
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        # Comments are sorted in chronological order
        self.create_comment(self.wl, self.tweet, '1')
        self.create_comment(self.wl_hsu, self.tweet, '2')
        self.create_comment(self.wl_hsu, self.create_tweet(self.wl_hsu), '3')
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(response.data['comments'][0]['content'], '1')
        self.assertEqual(response.data['comments'][1]['content'], '2')

        # Provide user_id and tweet_id at the same time,
        # only tweet_id will take effect in the filter
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'user_id': self.wl.id,
        })
        self.assertEqual(len(response.data['comments']), 2)

    def test_comments_count(self):
        # test tweet detail api
        tweet = self.create_tweet(self.wl)
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.wl_hsu_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments_count'], 0)

        # test tweet list api
        self.create_comment(self.wl, tweet)
        response = self.wl_hsu_client.get(TWEET_LIST_API, {'user_id': self.wl.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['comments_count'], 1)

        # test newsfeeds list api
        self.create_comment(self.wl_hsu, tweet)
        self.create_newsfeed(self.wl_hsu, tweet)
        response = self.wl_hsu_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['tweet']['comments_count'], 2)