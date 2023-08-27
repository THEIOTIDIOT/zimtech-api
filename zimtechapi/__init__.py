import logging
import logging.config
import yaml
from pathlib import Path
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy_utils import database_exists, create_database
from werkzeug.middleware.proxy_fix import ProxyFix

PROJECTROOT = Path(__name__).parent.resolve()

# class MyLogger(logging.Logger):
#     def __init__(self, name: str) -> None:
#         super().__init__(name=name)
#         # Setting some package specific customizations
#         # (Just aligns the logger for better legibility)
#         logging.addLevelName(logging.CRITICAL, "CRITICAL".ljust(8))
#         logging.addLevelName(logging.ERROR, "ERROR".ljust(8))
#         logging.addLevelName(logging.WARNING, "WARNING".ljust(8))
#         logging.addLevelName(logging.INFO, "INFO".ljust(8))
#         logging.addLevelName(logging.DEBUG, "DEBUG".ljust(8))
#         logging.addLevelName(logging.NOTSET, "NOTSET".ljust(8))


# # Setting the custom logger class to the default
# logging.setLoggerClass(MyLogger)


# def config_logger_options():
#     # Parse YAML config as dict and configure logging system
#     with open(Path(PROJECTROOT, "logger_config.yml").resolve(), "r") as f:
#         config = dict(yaml.safe_load(f))
#         logging.config.dictConfig(config)


# config_logger_options()

db = SQLAlchemy()
migrate = Migrate()

def create_app(
    config: str,
    origins: list = []
):
    # Initialize variables
    app = Flask(__name__)
    app.config.from_object(config)

    # Check if database exists, if not create it
    if not database_exists(app.config.get("SQLALCHEMY_DATABASE_URI")):
        create_database(app.config.get("SQLALCHEMY_DATABASE_URI"))

    db.init_app(app)
    migrate.init_app(app, db)
    from .models import bcrypt
    bcrypt.init_app(app)

    # setup proxy config
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

    # # Extensions
    CORS(
        app,
        # resource={r"/*": {"origins": origins}},
        # origins=origins,
        supports_credentials=True,
    )
    # app.config["CORS_HEADERS"] = "Content-Type"
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='None',
    )


    # from .views import base_blueprint
    from .auth.views import auth_blueprint
    # app.register_blueprint(base_blueprint)
    app.register_blueprint(auth_blueprint)

    return app