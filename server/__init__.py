from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt

# Initialize variables
app = Flask(__name__)
app.config.from_object("server.config.DevelopmentConfig")

# Extensions
CORS(
    app,
    # resources=r'/*',
    # origins=["http://localhost:5173","http://localhost:5000","https://*.benzimmer.com"],
    origins=["http://127.0.0.1:5173","http://127.0.0.1:5000"],
    supports_credentials=True,
    # vary_header=False,
    # send_wildcard=True
)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from server.auth.views import auth_blueprint

# CORS(auth_blueprint)

app.register_blueprint(auth_blueprint)

from server.views import base_blueprint

app.register_blueprint(base_blueprint)

