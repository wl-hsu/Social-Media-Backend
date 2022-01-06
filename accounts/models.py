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


# 定义一个 profile 的 property 方法，植入到 User 这个 model 里
# 这样当我们通过 user 的一个实例化对象访问 profile 的时候，即 user_instance.profile
# 就会在 UserProfile 中进行 get_or_create 来获得对应的 profile 的 object
# 这种写法实际上是一个利用 Python 的灵活性进行 hack 的方法，这样会方便我们通过 user 快速
# 访问到对应的 profile 信息。
def get_profile(user):
    if hasattr(user, '_cached_user_profile'):
        return getattr(user, '_cached_user_profile')
    profile, _ = UserProfile.objects.get_or_create(user=user)
    # 使用 user 对象的属性进行缓存(cache)，避免多次调用同一个 user 的 profile 时
    # 重复的对数据库进行查询
    setattr(user, '_cached_user_profile', profile)
    return profile


# Added a profile property method to User Model for quick access
User.profile = property(get_profile)