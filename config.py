import os

class Config(object):
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:////db/codenames.data'
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SECRET = os.environ['SECRET']
  JWT_SECRET_KEY = os.environ['SECRET']