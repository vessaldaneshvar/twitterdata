"""
Api twitter object
"""

import os
import tweepy

API_KEY_TWITTER = os.environ.get("API_KEY_TWITTER")
API_KEY_SECRET_TWITTER = os.environ.get("API_KEY_SECRET_TWITTER")
ACCESS_TOKEN_TWITTER = os.environ.get("ACCESS_TOKEN_TWITTER")
ACCESS_TOKEN_SECRET_TWITTER = os.environ.get("ACCESS_TOKEN_SECRET_TWITTER")

auth = tweepy.OAuthHandler(API_KEY_TWITTER, API_KEY_SECRET_TWITTER)
auth.set_access_token(ACCESS_TOKEN_TWITTER, ACCESS_TOKEN_SECRET_TWITTER)
api = tweepy.API(auth, wait_on_rate_limit=True)




