from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt

# Initialize variables
app = Flask(__name__)
CORS(app)

app.config.from_object('project.server.config.DevelopmentConfig')

# Extensions
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
migrate = Migrate(app, db)

from project.server.auth.views import auth_blueprint
app.register_blueprint(auth_blueprint)