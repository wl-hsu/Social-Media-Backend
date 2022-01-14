from django_hbase import models


class HBaseFollowing(models.HBaseModel):
    """
    Store who has been followed by from_user_id, row_key is sorted by from_user_id + created_at
    support query：
     - All people followed by A are sorted by follow time
     - Who did A follow during a certain time period?
     - Who are the top X people that A follows after/before a certain point in time
    """
    # row key
    from_user_id = models.IntegerField(reverse=True)
    created_at = models.TimestampField()
    # column key
    to_user_id = models.IntegerField(column_family='cf')

    class Meta:
        table_name = 'twitter_followings'
        row_key = ('from_user_id', 'created_at')


class HBaseFollower(models.HBaseModel):
    """
    Store to_user_id who has been followed, row_key is sorted by to_user_id + created_at
    support query：
     - All followers of A sorted by follow time
     - which followers A has been following during a certain period of time
     - Which X people followed A after/before a certain point in time
    """
    # row key
    to_user_id = models.IntegerField(reverse=True)
    created_at = models.TimestampField()
    # column key
    from_user_id = models.IntegerField(column_family='cf')

    class Meta:
        row_key = ('to_user_id', 'created_at')
        table_name = 'twitter_followers'