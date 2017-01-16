from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, PickleType
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from urllib.request import urlretrieve
from uuid import uuid4
import pickle
import pathlib

from settings import db_file, cache_pwd, config_pwd
import auth



engine = create_engine(db_file)

Session = sessionmaker(bind=engine)

Base = declarative_base()




class User(Base):
  __tablename__ = "users"

  id          = Column(Integer, primary_key=True)
  twitter_id  = Column(Integer, unique=True)
  screen_name = Column(String(50), unique=True)
  name        = Column(String(100))
  # tweets

  @property
  def config(self):
    fn = config_pwd/str(self.twitter_id)
    if not fn.is_file():
      return None
    return pickle.load(open(str(fn), "rb"))

  @config.setter
  def config(self, cfg):
    fn = config_pwd/str(self.twitter_id)
    pickle.dump(cfg, open(str(fn), "wb"))

  def __repr__(self):
    return "<User @{} ({}) with id {}>".format(self.screen_name, self.name, self.twitter_id)



class Tweet(Base):
  __tablename__ = "tweets"

  id          = Column(Integer, primary_key=True)
  twitter_id  = Column(Integer, unique=True)
  author_id   = Column(Integer, ForeignKey(User.id))
  author      = relationship(User, backref="tweets")
  text        = Column(String(200))
  answered    = Column(Boolean)
  # images

  def __repr__(self):
    return "<Tweet {} from user {} with id {}>".format(
      self.text if len(self.text)<=40 else self.text[:40]+"...",
      self.author,
      self.twitter_id
    )



class Image(Base):
  __tablename__ = "images"

  id          = Column(Integer, primary_key=True)
  url         = Column(String(100))
  filename    = Column(String(100)) # will be generated at get_image
  tweet_id    = Column(Integer, ForeignKey(Tweet.id))
  tweet       = relationship(Tweet, backref="images")

  def get_image(self):
    if not self.filename:
      self.filename = str(uuid4())+".jpg"
    fn = cache_pwd/self.filename
    if not fn.is_file():
      urlretrieve(self.url,str(fn))
    return str(fn)

  def __repr__(self):
    return "<Image from tweet {} saved in file: {}>".format(self.tweet.twitter_id,
      self.filename if (cache_pwd/self.filename).is_file() else "(None)")



class Response(Base):
  __tablename__ = "responses"

  id          = Column(Integer, primary_key=True)
  twitter_id  = Column(Integer, unique=True) # will be generated at send
  text        = Column(String(200))
  tweet_id    = Column(Integer, ForeignKey(Tweet.id))
  tweet       = relationship(Tweet, backref="response", uselist=False)
  # response_images

  def send(self):
    self.twitter_id = auth.api.update_status(
      self.text,
      media_ids=[e.send() for e in self.response_images],
      in_reply_to_status_id=self.tweet.twitter_id
    ).id

  def __repr__(self):
    return "<Response to tweet {}>".format(this.tweet.id)



class ResponseImage(Base):
  __tablename__ = "response_images"

  id          = Column(Integer, primary_key=True)
  filename    = Column(String(100)) # will be generated, shall be filled
  response_id = Column(Integer, ForeignKey(Response.id))
  response    = relationship(Response, backref="response_images")

  def get_image(self):
    if not self.filename:
      self.filename = str(uuid4())+".jpg"
    fn = cache_pwd/self.filename
    return str(fn)

  def send(self):
    return auth.api.media_upload(self.get_image()).media_id

  def __repr__(self):
    return "<Image from response {} saved in file: {}>".format(self.response.id, self.filename)

