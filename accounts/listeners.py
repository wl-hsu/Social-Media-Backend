def profile_changed(sender, instance, **kwargs):
    # import Write it in the function to avoid circular dependencies
    from accounts.services import UserService
    UserService.invalidate_profile(instance.user_id)