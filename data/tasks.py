from __future__ import absolute_import, unicode_literals

from .tweepy_API import app as twitter_api
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
    today_tweets = twitter_api.search(lang="fa", count=50, until=until_time.strftime("%Y-%m-%d"))

    # TODO: this function must be complete --> process tweets and save in the database
