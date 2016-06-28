import argparse
import csv
import tweepy
import config
from models import User
from sqlalchemy import create_engine
from models import Base
from sqlalchemy.orm import sessionmaker


def api_factory():
    auth = tweepy.OAuthHandler(config.consumer_token, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_token_secret)

    return tweepy.API(auth)


def session_factory():
    engine = create_engine('sqlite:///db.db', echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


args_parser = argparse.ArgumentParser()
args_parser.add_argument(
    "user_list", help="CSV file containing <source, user> pairs")
args = args_parser.parse_args()


with open(args.user_list) as inp:
    reader = csv.reader

    api = api_factory()
    session = session_factory()

    reader = csv.DictReader(inp)
    for row in reader:
        print('Querying user: {}'.format(row['user']))

        try:
            user_data = api.get_user(row['user'])
            print('{}: {}'.format(user_data.screen_name, user_data.id))
        except tweepy.error.TweepError:
            print('User {} not found'.format(row['user']))
            continue

        user = session.query(User).get(user_data.id)

        if user is None:
            user = User()

        user.id = user_data.id
        user.screen_name = user_data.screen_name
        user.friends_count = user_data.friends_count
        user.followers_count = user_data.followers_count

        session.add(user)
        session.commit()
