import logging
import logging.config
import yaml
from pathlib import Path
from flask import Flask
# from flask_script import Manager
from flask_cors import CORS
# from flask_migrate import Migrate
from api.views import base_blueprint
from api.auth.views import auth_blueprint

PROJECTROOT = Path(__name__).parent.resolve()

class MyLogger(logging.Logger):
    def __init__(self, name: str) -> None:
        super().__init__(name=name)
        # Setting some package specific customizations
        # (Just aligns the logger for better legibility)
        logging.addLevelName(logging.CRITICAL, "CRITICAL".ljust(8))
        logging.addLevelName(logging.ERROR, "ERROR".ljust(8))
        logging.addLevelName(logging.WARNING, "WARNING".ljust(8))
        logging.addLevelName(logging.INFO, "INFO".ljust(8))
        logging.addLevelName(logging.DEBUG, "DEBUG".ljust(8))
        logging.addLevelName(logging.NOTSET, "NOTSET".ljust(8))


# Setting the custom logger class to the default
logging.setLoggerClass(MyLogger)


def config_logger_options():
    # Parse YAML config as dict and configure logging system
    print(PROJECTROOT)
    with open(Path(PROJECTROOT, "logger_config.yml").resolve(), "r") as f:
        config = dict(yaml.safe_load(f))
        logging.config.dictConfig(config)


config_logger_options()

def create_app():
    # Initialize variables
    app = Flask(__name__)
    # app.config.from_object("server.config.DevelopmentConfig")
    app.config.from_object("api.config.DevelopmentConfig")


    # Extensions
    CORS(
        app,
        # origins=["http://127.0.0.1:5173","http://127.0.0.1:5000", "http://127.0.0.1:5555", "http://127.0.0.1:8080"],
        resource={
            r"/*":{
                "origins":["http://127.0.0.1:5173"]
            }
        },
        supports_credentials=True,
    )

    app.config['CORS_HEADERS'] = 'Content-Type'

    from api.models import db, bcrypt
    bcrypt.init_app(app)
    # manager = Manager(app)
    db.init_app(app)
    # migrate = Migrate(app, db)
    app.register_blueprint(base_blueprint)
    app.register_blueprint(auth_blueprint)
    return app