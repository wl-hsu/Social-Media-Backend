from friendships.models import Friendship


class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):

        # This way of writing will cause the problem of N + 1 Queries
        # That is, it takes a Query to filter out all friendships
        # And taking from_user for each friendship in the for loop takes N Queries
        # friendships = Friendship.objects.filter(to_user=user)
        # return [friendship.from_user for friendship in friendships]

        # This way of writing uses the JOIN operation to make the friendship table and user table in from_user
        # Join on this attribute. The join operation is disabled in the web scenario of large-scale users because it is very slow.
        # friendships = Friendship.objects.filter(
        #     to_user=user
        # ).select_related('from_user')
        # return [friendship.from_user for friendship in friendships]

        # The better way is that manually filter id, use IN Query to query
        # friendships = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        # followers = User.objects.filter(id__in=follower_ids)

        # Another better way is hat use prefetch_related，
        # It will be automatically executed into two statements, query with In Query
        # The actual SQL query executed is the same as above, there are two SQL Queries in total
        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]