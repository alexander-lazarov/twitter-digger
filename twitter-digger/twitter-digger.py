import argparse
import csv
import tweepy
import config
import re
from models import User, Tweet, Entity
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


def normalize_twitter(url):
    if re.match(r'^[A-Za-z0-9_]{1,15}$', url):
        return url

    if re.match(r'^@[A-Za-z0-9_]{1,15}$', url):
        return url[1:]

    match = re.match(
        r'^https?://(www\.)?twitter.com/([A-Za-z0-9_]{1,15})$', url)

    if match:
        return match.group(2)

    return ''


class Downloader():
    def __init__(self, api, session):
        self.api = api
        self.session = session

    def handle_user(self, username):
        username = normalize_twitter(username)
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
        self.session.add(user)
        self.session.commit()

    def _handle_tweets(self, user):

        try:
            tweets = self.api.user_timeline(user.screen_name, count=200)
        except tweepy.error.TweepError:
            print('Error downloading tweets for {}'.format(user.screen_name))

        for tweet_data in tweets:
            tweet = self.session.query(Tweet).get(tweet_data.id)

            if tweet is None:
                tweet = Tweet()
                is_new = True
            else:
                is_new = False

            tweet.id = tweet_data.id
            tweet.text = tweet_data.text
            tweet.retweet_count = tweet_data.retweet_count
            tweet.user = user

            self.session.add(tweet)
            self.session.commit()

            if is_new:
                print('Saving entities for tweet {}'.format(tweet.id))
                self._handle_entities(tweet, tweet_data)
                self.session.commit()
            else:
                print('Skipping entities for tweet {}'.format(tweet.id))

        print('Downloaded {} tweets for user {}'.format(
            len(tweets), user.screen_name))

        self.session.commit()

    def _handle_entities(self, tweet, tweet_data):
        for category in tweet_data.entities:
            for entity_data in tweet_data.entities[category]:
                content = ''

                if category == 'urls':
                    content = entity_data['expanded_url']
                if category == 'hashtags':
                    content = entity_data['text']
                if category == 'user_mentions':
                    content = entity_data['screen_name']

                entity = Entity(
                    category=category, tweet=tweet, content=content)
                self.session.add(entity)


with open(args.user_list) as inp:
    reader = csv.reader

    api = api_factory()
    session = session_factory()

    downloader = Downloader(api, session)

    reader = csv.DictReader(inp)
    for row in reader:
        downloader.handle_user(row['user'])
