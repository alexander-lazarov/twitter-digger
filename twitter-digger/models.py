from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    screen_name = Column(String)
    friends_count = Column(Integer)
    followers_count = Column(Integer)
    tweets = relationship('Tweet', back_populates='user')


class Tweet(Base):
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='tweets')
    text = Column(String)
    retweet_count = Column(Integer)
    entities = relationship('Entity', back_populates='tweet')


class Entity(Base):
    __tablename__ = 'entities'

    id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer, ForeignKey('tweets.id'))
    tweet = relationship('Tweet', back_populates='entities')
    category = Column(String)
    content = Column(String)
