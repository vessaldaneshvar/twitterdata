from __future__ import absolute_import, unicode_literals

from django.db.models import F
from .tweepy_API import api as twitter_api
from .models import TwitterUser, TwitterStatus
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
    json_status["tweet_id"] = json_status.pop("id")
    # User of tweet get or create
    user_json = json_status.pop('user')
    user_json['userid'] = user_json.pop('id')
    created_at_user = user_json.get("created_at", datetime.datetime.now().strftime("%a %b %d %X %z %Y"))
    created_at_user = datetime.datetime.strptime(created_at_user, "%a %b %d %X %z %Y")
    user_json["created_at"] = created_at_user
    json_status['user'] = TwitterUser.objects.get_or_create(**user_json)
    json_status['user']
    if json_status.get('quoted_status', None):
        process_tweet_for_model(json_status.get('quoted_status'))
    if json_status.get('retweeted_status', None):
        process_tweet_for_model(json_status.get('retweeted_status'))

    TwitterStatus.objects.get_or_create(**json_status)
    