import tweepy
import settings

_auth = tweepy.OAuthHandler(settings.consumer_key, settings.consumer_secret)
_auth.set_access_token(settings.token, settings.token_secret)
api = tweepy.API(_auth)
