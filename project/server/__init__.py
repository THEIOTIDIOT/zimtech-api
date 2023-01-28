from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt

# Initialize variables
app = Flask(__name__)
app.config.from_object('project.server.config.DevelopmentConfig')

# Extensions
CORS(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from project.server.auth.views import auth_blueprint
app.register_blueprint(auth_blueprint)

from project.server.views import base_blueprint
app.register_blueprint(base_blueprint)