def invalidate_following_cache(sender, instance, **kwargs):
    # import Write it in the function to avoid circular dependencies
    from friendships.services import FriendshipService
    FriendshipService.invalidate_following_cache(instance.from_user_id)