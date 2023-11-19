import configparser
import logging
from flask_security import (
    SmsSenderFactory,
    SmsSenderBaseClass,
    uia_phone_mapper,
    uia_email_mapper,
)
import datetime

logger = logging.getLogger(__name__)

# Config variables
parser = configparser.ConfigParser()
parser.read("config.ini")
username = parser["postgres"]["username"]
password = parser["postgres"]["password"]
server_host = parser["postgres"]["server_host"]
db_name = parser["postgres"]["db_name"]
secret_key = parser["flask"]["secret_key"]
password_salt = parser["flask"]["password_salt"]
totp_secret = parser["flask"]["totp_secret"]
smtp_email = parser["flask"]["smtp_email"]
smtp_password = parser["flask"]["smtp_password"]
postgres_connection = f"postgresql://{username}:{password}@{server_host}/{db_name}"


class BaseConfig:
    """Base configuration."""

    SECRET_KEY = secret_key
    DEBUG = False
    SECURITY_PASSWORD_SALT = password_salt
    SECURITY_FLASH_MESSAGES = False
    SECURITY_USER_IDENTITY_ATTRIBUTES = [
        {"email": {"mapper": uia_email_mapper, "case_insensitive": True}},
        {"us_phone_number": {"mapper": uia_phone_mapper}},
    ]
    SECURITY_US_ENABLED_METHODS = ["password", "email", "sms"]

    SECURITY_TOTP_SECRETS = {"1": totp_secret}

    # These need to be defined to handle redirects
    # As defined in the API documentation - they will receive the relevant context
    SECURITY_POST_CONFIRM_VIEW = "/confirmed"
    SECURITY_CONFIRM_ERROR_VIEW = "/confirm-error"
    SECURITY_RESET_VIEW = "/reset-password"
    SECURITY_RESET_ERROR_VIEW = "/reset-password-error"
    SECURITY_REDIRECT_BEHAVIOR = "spa"

    # CSRF protection is critical for all session-based browser UIs
    # In general, most applications don't need CSRF on unauthenticated endpoints
    # API calls to go through
    SECURITY_CSRF_PROTECT_MECHANISMS = ["session", "basic"]
    SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS = True

    # Send Cookie with csrf-token. This is the default for Axios and Angular.
    SECURITY_CSRF_COOKIE_NAME = "XSRF-TOKEN"
    WTF_CSRF_CHECK_DEFAULT = False
    WTF_CSRF_TIME_LIMIT = None

    # have session and remember cookie be samesite (flask/flask_login)
    REMEMBER_COOKIE_SAMESITE = "strict"
    SESSION_COOKIE_SAMESITE = "strict"

    # This means the first 'fresh-required' endpoint after login will always require
    # re-verification - but after that the grace period will kick in.
    # This isn't likely something a normal app would need/want to do.
    SECURITY_FRESHNESS = datetime.timedelta(minutes=0)
    SECURITY_FRESHNESS_GRACE_PERIOD = datetime.timedelta(minutes=2)

    # As of Flask-SQLAlchemy 2.4.0 it is easy to pass in options directly to the
    # underlying engine. This option makes sure that DB connections from the pool
    # are still valid. Important for entire application since many DBaaS options
    # automatically close idle connections.
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Initialize a fake SMS service that captures SMS messages
    SECURITY_SMS_SERVICE = "capture"
    # SmsSenderFactory.senders["capture"] =

    # Mail Server
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = smtp_email
    MAIL_PASSWORD = smtp_password
    MAIL_DEFAULT_SENDER = smtp_email
    MAIL_BACKEND = "smtp"
    AUTH_METHODS = ["session"]


class TestDevConfig(BaseConfig):
    """Base for both test and dev configs"""

    DEBUG = True
    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = True
    WTF_CSRF_ENABLED = False
    # Our test emails/domain isn't necessarily valid
    SECURITY_EMAIL_VALIDATOR_ARGS = {"check_deliverability": False}
    # Make this plaintext for most tests - reduces unit test time by 50%
    SECURITY_PASSWORD_HASH = "plaintext"


class TestingConfig(TestDevConfig):
    """Testing configuration."""

    SQLALCHEMY_DATABASE_URI = postgres_connection + "_test"
    # Allow registration of new users without confirmation
    SECURITY_REGISTERABLE = True
    AUTH_METHODS = ["session", "token"]


class DevelopmentConfig(TestDevConfig):
    """Development configuration."""

    SQLALCHEMY_DATABASE_URI = postgres_connection + "_dev"
    SECURITY_REDIRECT_HOST = "localhost:5173"


class ProductionConfig(BaseConfig):
    """Production configuration."""

    SQLALCHEMY_DATABASE_URI = postgres_connection
    # SESSION_COOKIE_DOMAIN = '.benzimmer.us'
    # SESSION_COOKIE_SECURE = True
