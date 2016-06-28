from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    screen_name = Column(String)
    friends_count = Column(Integer)
    followers_count = Column(Integer)
