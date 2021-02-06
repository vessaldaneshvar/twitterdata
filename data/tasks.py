from __future__ import absolute_import, unicode_literals

from django.db.models import F
import tweepy
from .tweepy_API import api as twitter_api
from .list_words import list_persian_common_words
from .models import TwitterUser, TwitterStatus, TrackUser
from config.celery import app
import datetime

today = datetime.datetime.now()
one_day_timedelta = datetime.timedelta(days=1)

@app.task
def get_most_popular_persian_tweets():
    """
    this function get favorited tweet every day
    this is scheduled by celery task beat
    """
    until_time = today-one_day_timedelta
    today_tweets = twitter_api.search(
        q="",
        lang="fa",
        count=50,
        until=until_time.strftime("%Y-%m-%d"),
    )

    # TODO: this function must be complete --> process tweets and save in the database

@app.task
def get_tweets_of_popular_person():
    """
    This function get tweet of popular person every day
    condition of this person :: followers > 20000 AND following < followers/10 AND status_count > 2000
    and top 50 of this list was in query
    this is scheduled by celery task beat
    """
    
    popular_person = TwitterUser.objects.filter(
        statuses_count__gte = 2000,
        followers_count__gte = 20000,
        friends_count__gt = F("followers_count") / 10 ,
    )
    query_twitter = ""
    for person in popular_person.all():
        if len(query_twitter) > 450:
            break
            # TODO : send request for other person
        query_twitter += f"from:{person.screen_name} OR "

    # Other condition
    query_twitter = query_twitter[:-3]
    query_twitter += "AND -filter:retweets"

    tweets = twitter_api.search(
        q=query_twitter,
        lang="fa",
        count=100,
    )
    for tweet in tweets:
        process_tweet_for_model(tweet._json)

    
def process_tweet_for_model(json_status):
    '''
    This function process json and convert data for TwitterStatus model
    '''

    created_at_status = json_status.get("created_at", datetime.datetime.now().strftime("%a %b %d %X %z %Y"))
    created_at_status = datetime.datetime.strptime(created_at_status, "%a %b %d %X %z %Y")
    json_status["created_at"] = created_at_status
    tweet_id = json_status.pop("id")
    # User of tweet get or create
    user_json = json_status.pop('user')
    userid = user_json.pop('id')
    created_at_user = user_json.get("created_at", datetime.datetime.now().strftime("%a %b %d %X %z %Y"))
    created_at_user = datetime.datetime.strptime(created_at_user, "%a %b %d %X %z %Y")
    user_json["created_at"] = created_at_user
    json_status['user'], created = TwitterUser.objects.get_or_create(userid=userid, defaults=user_json)
    if json_status.get('quoted_status', None):
        process_tweet_for_model(json_status.get('quoted_status'))
    if json_status.get('retweeted_status', None):
        process_tweet_for_model(json_status.get('retweeted_status'))

    TwitterStatus.objects.get_or_create(tweet_id=tweet_id, defaults=json_status)


@app.task
def update_user_property_popular_person():
    """
    This Function lookup 10000 person of Users order by followers
    Also this data don't update and save in new models
    model for this data is TrackUser
    """

    users = TwitterUser.objects.filter().order_by("followers_count")[:10000]
    list_user_id = []
    for user in users:
        list_user_id.append(user.userid)
        if len(list_user_id) == 100:
            response_users = twitter_api.lookup_users(user_ids=list_user_id)
            save_users_list_track_model(response_users)
            list_user_id = []


            
def save_users_list_track_model(resp):
    """
    input of this function is lookup/users response
    this function save users in TrackUser models such as json object
    """
    for user in resp:
        json_user = user._json
        TrackUser.objects.create(
            user=json_user
        )


class StreamPersianTweets(tweepy.StreamListener):

    def on_status(self, status):
        try:
            self.counter += 1
        except:
            self.counter = 1

        if self.check_condition_stream_user_save(status._json.get("user")):
            self.save_user_in_db(status._json.get("user"))
        if self.counter % 1000 == 1:
            print(self.counter)

    def check_condition_stream_user_save(self, user_json):
        """
        check user followers > 250
        """
        if user_json.get("followers_count", 0) > 250:
            return True
        return False

    def save_user_in_db(self, user_json):
        """
        Save Data in model TwitterUser
        """
        userid = user_json.pop('id')
        created_at = user_json.get("created_at", datetime.datetime.now().strftime("%a %b %d %X %z %Y"))
        created_at = datetime.datetime.strptime(created_at, "%a %b %d %X %z %Y")
        user_json["created_at"] = created_at
        default_data = {}
        default_data["id_str"] = user_json.get("id_str")
        default_data["name"] = user_json.get("name")
        default_data["screen_name"] = user_json.get("screen_name")
        default_data["location"] = user_json.get("location", "")
        default_data["url"] = user_json.get("url")
        default_data["description"] = user_json.get("description")
        default_data["protected"] = user_json.get("protected")
        default_data["verified"] = user_json.get("verified")
        default_data["followers_count"] = user_json.get("followers_count")
        default_data["friends_count"] = user_json.get("friends_count")
        default_data["listed_count"] = user_json.get("listed_count")
        default_data["favourites_count"] = user_json.get("favourites_count")
        default_data["statuses_count"] = user_json.get("statuses_count")
        default_data["created_at"] = user_json.get("created_at")
        default_data["profile_banner_url"] = user_json.get("profile_banner_url")
        default_data["profile_image_url_https"] = user_json.get("profile_image_url_https")
        TwitterUser.objects.get_or_create(userid=userid, defaults=default_data)

    def on_error(self, status_code):
        print(status_code)
        return False

def get_stream_data_and_save_users():
    """
    This function get Every Persian Tweets but not save all tweets
    and just save users where followers > 250
    this function called in StartUp of data App
    """
    stream_obj = tweepy.Stream(auth=twitter_api.auth, listener=StreamPersianTweets())
    stream_obj.filter(languages=["fa"], track=list_persian_common_words)