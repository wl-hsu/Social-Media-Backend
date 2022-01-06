from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    # One2One field will create a unique index to ensure that no multiple UserProfiles point to the same User
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    # Django also has an ImageField, but try not to use it. There will be many other problems.
    # Using FileField can achieve the same effect.
    # Because in the end we are all stored in the form of files, using the url of the file for access
    avatar = models.FileField(null=True)
    # When a user is created, an object of user profile will be created. At this time,
    # the user has no time to set nickname and other information, so set null=True
    nickname = models.CharField(null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {}'.format(self.user, self.nickname)


# Define the property method of a profile and embed it in the User model
# So when we access the profile through an instantiated object of user, that is,
# user_instance.profile will get_or_create in UserProfile to obtain the corresponding profile object
# This writing method is actually a method of hacking using the flexibility of Python,
# which will facilitate us to quickly access the corresponding profile information through the user.
def get_profile(user):
    if hasattr(user, '_cached_user_profile'):
        return getattr(user, '_cached_user_profile')
    profile, _ = UserProfile.objects.get_or_create(user=user)
    # Use the attributes of the user object to cache (cache) to avoid repeated queries to the database
    # when the profile of the same user is called multiple times
    setattr(user, '_cached_user_profile', profile)
    return profile


# Added a profile property method to User Model for quick access
User.profile = property(get_profile)