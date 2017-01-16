#!/usr/bin/env python3
from tweepy import Cursor
from auth import api
from models import Session, User, Tweet, Image, Response, ResponseImage
from sqlalchemy import func
from processor import TweetProcessor
import datetime

s = Session()


def parse_tweet(raw_tweet):
  if s.query(Tweet).filter_by(twitter_id=raw_tweet.id).first():
    s.close()

  user = s.query(User).filter_by(twitter_id=raw_tweet.user.id).first()
  if not user:
    user = User(
      twitter_id=raw_tweet.user.id,
      screen_name=raw_tweet.user.screen_name,
      name=raw_tweet.user.name)
    s.add(user)

  if s.query(Tweet).filter_by(twitter_id=raw_tweet.id).first():
    s.rollback()
    return

  tweet = Tweet(twitter_id=raw_tweet.id, author=user, text=raw_tweet.text, answered=False)
  s.add(tweet)

  if "media" in raw_tweet.extended_entities:
    for pic in raw_tweet.extended_entities["media"]:
      if pic["type"] != "photo":
        continue
      img = Image(url=pic["media_url"], filename="", tweet=tweet)
      s.add(img)
  s.commit()


def answer_tweet(t_id):
  tweet = s.query(Tweet).get(t_id)
  author = tweet.author

  processor = TweetProcessor(text=tweet.text, state=author.config, author = author.screen_name)
  tweet.answered = True
  if len(tweet.images) == 0 or not processor.should_process():
    s.commit()
    print("Busted!")
    return
    print("Answering...")



  resp = Response(text=processor.response(), tweet=tweet)
  s.add(resp)
  for img in tweet.images:
    ri = ResponseImage(response=resp)
    processor.generate_image(ri.get_image(), img.get_image())
    s.add(ri)
  resp.send()
  author.config = processor.updated_config()
  s.commit()


def crawl():
  print(datetime.datetime.now(), "crawling")
  max_id = s.query(func.max(Tweet.twitter_id)).first()[0]

  for raw_tweet in Cursor(api.mentions_timeline, since_id=max_id, include_entities=True).items():
    print("downloading tweet", raw_tweet.id)
    parse_tweet(raw_tweet)
  for tweet in s.query(Tweet).filter_by(answered=False).all():
    print("answering tweet", tweet.twitter_id)
    answer_tweet(tweet.id)



if __name__ == "__main__":
  crawl()
