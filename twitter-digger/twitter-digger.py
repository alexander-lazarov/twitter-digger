import argparse
import csv
import tweepy
import config
from models import User, Tweet
from sqlalchemy import create_engine
from models import Base
from sqlalchemy.orm import sessionmaker


def api_factory():
    auth = tweepy.OAuthHandler(config.consumer_token, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_token_secret)

    return tweepy.API(auth)


def session_factory():
    engine = create_engine('sqlite:///db.db', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


args_parser = argparse.ArgumentParser()
args_parser.add_argument(
    "user_list", help="CSV file containing <source, user> pairs")
args = args_parser.parse_args()


class Downloader():
    def __init__(self, api, session):
        self.api = api
        self.session = session

    def handle_user(self, username):
        print('Querying user: {}'.format(username))

        try:
            user_data = self.api.get_user(username)
        except tweepy.error.TweepError:
            print('User {} not found'.format(username))
            return

        user = self.session.query(User).get(user_data.id)

        if user is None:
            user = User()

        user.id = user_data.id
        user.screen_name = user_data.screen_name
        user.friends_count = user_data.friends_count
        user.followers_count = user_data.followers_count

        self._handle_tweets(user)

    def _handle_tweets(self, user):
        tweets = self.api.user_timeline(row['user'], count=200)
        for tweet_data in tweets:
            tweet = self.session.query(Tweet).get(tweet_data.id)

            if tweet is None:
                tweet = Tweet()

            tweet.id = tweet_data.id
            tweet.text = tweet_data.text
            tweet.retweet_count = tweet_data.retweet_count
            tweet.user = user

            self.session.add(tweet)

        print('Downloaded {} tweets for user {}'.format(
            len(tweets), user.screen_name))

        self.session.add(user)
        self.session.commit()


with open(args.user_list) as inp:
    reader = csv.reader

    api = api_factory()
    session = session_factory()

    downloader = Downloader(api, session)

    reader = csv.DictReader(inp)
    for row in reader:
        downloader.handle_user(row['user'])
