from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_wtf.csrf import CSRFProtect, generate_csrf


# Initialize variables
app = Flask(__name__)
app.config.from_object('project.server.config.DevelopmentConfig')
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.session_protection = "strong"

# Extensions
CORS(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

from project.server.auth.views import auth_blueprint
app.register_blueprint(auth_blueprint)