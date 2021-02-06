from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
# Create your models here.

class TwitterUser(models.Model):
    '''
    this models define twitter users
    docs : https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/user
    '''

    class Meta:
        verbose_name = 'Twitter User'
        verbose_name_plural = 'Twitter Users'

    userid = models.BigIntegerField(verbose_name="id", unique=True)
    id_str = models.CharField(max_length=20, unique=True, verbose_name="id_str")
    name = models.CharField(max_length=200, verbose_name="name")
    screen_name = models.CharField(max_length=200, verbose_name="screen_name")
    location = models.CharField(max_length=200, blank=True, null=True)
    url = models.SlugField(verbose_name="url", blank=True, null=True, max_length=500)
    description = models.CharField(max_length=2000, verbose_name="description", blank=True, null=True)
    protected = models.BooleanField(verbose_name="protected")
    verified = models.BooleanField(verbose_name="verified")
    followers_count = models.IntegerField(verbose_name="followers_count")
    friends_count = models.IntegerField(verbose_name="friends_count")
    listed_count = models.IntegerField(verbose_name="listed_count")
    favourites_count = models.IntegerField(verbose_name="favourites_count")
    statuses_count = models.IntegerField(verbose_name="statuses_count")
    created_at = models.DateTimeField(verbose_name="created_at")
    profile_banner_url = models.SlugField(verbose_name="profile_banner_url", max_length=500, blank=True, null=True)
    profile_image_url_https = models.SlugField(verbose_name="profile_image_url_https", max_length=500, blank=True, null=True)

    def __str__(self):
        return self.screen_name

class TwitterStatus(models.Model):
    '''
    define status of twitter --> in other words Tweet
    document of this models in twitter docs is :
    https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/tweet
    '''

    class Meta:
        verbose_name = 'Status'
        verbose_name_plural = 'Statuses'

    created_at = models.DateTimeField(verbose_name="created_at")
    tweet_id = models.BigIntegerField(verbose_name="id")
    id_str = models.CharField(max_length=20, verbose_name="id_str")
    text = models.CharField(max_length=1000, verbose_name="text")
    source = models.CharField(max_length=100)
    truncated = models.BooleanField(verbose_name="truncated")
    in_reply_to_status_id = models.BigIntegerField(verbose_name="in_reply_to_status_id", blank=True, null=True)
    in_reply_to_user_id = models.BigIntegerField(verbose_name="in_reply_to_user_id", blank=True, null=True)
    in_reply_to_screen_name = models.CharField(max_length=200, verbose_name="in_reply_to_screen_name", blank=True, null=True)
    user = models.ForeignKey(TwitterUser, on_delete=models.CASCADE, verbose_name="user")
    id_quoted_status = models.BigIntegerField(verbose_name="quoted_status_id", blank=True, null=True)
    is_quote_status = models.BooleanField(verbose_name="is_quote_status")
    quoted_status = models.ForeignKey("TwitterStatus", on_delete=models.CASCADE, verbose_name="quoted_status", related_name="quoted", blank=True, null=True)
    retweeted_status = models.ForeignKey("TwitterStatus", on_delete=models.CASCADE, verbose_name="retweeted_status", related_name="retweeted", blank=True, null=True)
    quote_count = models.IntegerField(verbose_name="quote_count", blank=True, null=True)
    reply_count = models.IntegerField(verbose_name="reply_count", blank=True, null=True)
    retweet_count = models.IntegerField(verbose_name="retweet_count", blank=True, null=True)
    favorite_count = models.IntegerField(verbose_name="favorite_count", blank=True, null=True)
    lang = models.CharField(max_length=30, verbose_name="language", blank=True, null=True)
    entities = JSONField(verbose_name="entities")

    def __str__(self):
        return self.id_str


class TrackUser(models.Model):

    class Meta:
        verbose_name = "Track User"
        verbose_name_plural = "Track Users"
    
    user = JSONField(verbose_name="user json")
    track_time = models.DateTimeField(verbose_name="time saved data", default=timezone.now())