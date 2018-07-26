from cryptography.fernet import Fernet
import os
from datetime import datetime, time, timedelta, timezone


class BaseConfig(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@db/postgres'
    SECRET_KEY = Fernet.generate_key()
    WINNERS_NUM = 90
    RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')
    TIMEZONE = timezone(timedelta(hours=+9), 'JST')
    START_DATETIME = datetime(2018, 9, 16, 8,  40, 0, tzinfo=TIMEZONE)
    END_DATETIME = datetime(2018, 9, 17, 16, 00, 0, tzinfo=TIMEZONE)
    DRAWING_TIME_EXTENSION = timedelta(minutes=10)
    TIMEPOINTS = [
        (time(9,  20), time(9,  50)),
        (time(10, 45), time(11, 15)),
        (time(12, 10), time(12, 40)),
        (time(13, 35), time(14,  5)),
    ]


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    ENV = 'development'


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    ENV = 'development'
    WINNERS_NUM = 3  # just small value
    # Recaptcha test key for automated testing.
    # https://developers.google.com/recaptcha/docs/faq#id-like-to-run-automated-tests-with-recaptcha-v2-what-should-i-do
    RECAPTCHA_SECRET_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'


class PreviewDeploymentConfig(BaseConfig):
    DEBUG = True
    TESTING = False
    # DATABASE_URL is to be set by Heroku
    # SECRET_KEY is to be set in config vars
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ENV = 'development'


class DeploymentConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    # None, to be configured in config.cfg in instance directory
    SQLALCHEMY_DATABASE_URI = None
    SECRET_KEY = None
    ENV = 'production'
