import configparser
import logging

logger = logging.getLogger(__name__)

# Config variables
parser = configparser.ConfigParser()
parser.read("config.ini")
username = parser["postgres"]["username"]
password = parser["postgres"]["password"]
server_host = parser["postgres"]["server_host"]
db_name = parser["postgres"]["db_name"]
secret_key = parser["flask"]["secret_key"]
postgres_connection = f"postgresql://{username}:{password}@{server_host}/{db_name}"

class BaseConfig:
    """Base configuration."""
    SECRET_KEY = secret_key
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    def __init__(self):
        super().__init__()
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = postgres_connection


class TestingConfig(BaseConfig):
    """Testing configuration."""
    def __init__(self):
        super().__init__()
    SECRET_KEY = secret_key
    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = postgres_connection + "_test"
    PRESERVE_CONTEXT_ON_EXCEPTION = True


class ProductionConfig(BaseConfig):
    """Production configuration."""
    def __init__(self):
        super().__init__()
    SECRET_KEY = secret_key
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = postgres_connection