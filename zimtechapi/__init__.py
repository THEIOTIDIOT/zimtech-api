import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy_utils import database_exists, create_database
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_security import Security
from flask_wtf import CSRFProtect
from .models import db, user_datastore, Blog
from flask_mailman import Mail

migrate: Migrate = Migrate()
security: Security = Security()
mail: Mail = Mail()

def create_app(
    config: str,
    origins: list = ["*"]
) -> Flask:
    # Initialize variables
    app = Flask(__name__)
    app.config.from_object(config)
    # Turn on all features (except passwordless since that removes normal login)
    for opt in [
        "changeable",
        "recoverable",
        "registerable",
        "trackable",
        "confirmable",
        "two_factor",
        "unified_signin",
    ]:
        app.config["SECURITY_" + opt.upper()] = True

    # Check if database exists, if not create it
    if not database_exists(app.config.get("SQLALCHEMY_DATABASE_URI")):
        create_database(app.config.get("SQLALCHEMY_DATABASE_URI"))

    # Extension inits
    db.init_app(app)
    migrate.init_app(app, db)
    CSRFProtect(app)
    # security.init_app(app, user_datastore)
    app.security = Security(app, user_datastore)
    mail.init_app(app)

    # setup proxy config
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

    # Extensions
    CORS(
        app,
        origins=origins,
        supports_credentials=True,
    )

    # from .views import base_blueprint
    from .api import api

    # app.register_blueprint(base_blueprint)
    app.register_blueprint(api, url_prefix="/api")

    return app