import datetime
import time
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from project.server import app, db, bcrypt
from flask_login import UserMixin
from flask_wtf.csrf import generate_csrf
import sqlalchemy as sa
from project.util import AESCipher


class WebAppUser(db.Model, UserMixin):
    """User Model for storing user related details"""

    __tablename__ = "WEB_APP_USER"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    username = sa.Column(sa.String(255), unique=True, nullable=False)
    email = sa.Column(sa.String(255), unique=True, nullable=False)
    password = sa.Column(sa.String(255), nullable=False)
    registered_on = sa.Column(sa.DateTime, nullable=False)
    admin = sa.Column(sa.Boolean, nullable=False, default=False)

    def __init__(self, username, email, password, admin=False):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get("BCRYPT_LOG_ROUNDS")
        ).decode()
        self.registered_on = datetime.datetime.now()
        self.admin = admin

class WebAppUserSession(db.Model):
    """Web App User Session Model for storing user sessions"""

    __tablename__ = "WEB_APP_USER_SESSION"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(WebAppUser.id), nullable=False)
    csrf_token = sa.Column(sa.String(255), unique=True, nullable=False)
    csrf_token_create_datetime = sa.Column(sa.DateTime, nullable=False)
    csrf_token_expiration_datetime = sa.Column(sa.DateTime, nullable=False)
    csrf_token_disabled = sa.Column(sa.Boolean, nullable=False)

    def __init__(self, email, session_length_mins):
        user = db.session.execute(sa.select(WebAppUser).filter_by(email=email)).scalar_one()
        self.user_id = user.id
        now = datetime.datetime.now()
        self.csrf_token_expiration_datetime = now + datetime.timedelta(minutes=session_length_mins)
        cipher = AESCipher(app.config.get("SECRET_KEY"))
        token = cipher.encrypt(f"{user.username}{now}")
        self.csrf_token = token
        self.csrf_token_create_datetime = now
        self.csrf_token_disabled = False

    @staticmethod
    def is_session_active(email):
        user_session = WebAppUserSession.get_active_user_session(email)
        if user_session != None:
            if datetime.datetime.now() > user_session.csrf_token_expiration_datetime:
                return False
            else:
                return True
        else:
            return False

    @staticmethod
    def get_active_user_session(email : str) -> 'WebAppUserSession' : 
        user = WebAppUser.query.where(WebAppUser.email==email).first()
        
        user_session = (
            WebAppUserSession.query.where(
                WebAppUserSession.user_id==user.id, 
                WebAppUserSession.csrf_token_disabled==False,
            )
            .order_by(
                WebAppUserSession.csrf_token_create_datetime.desc()
            ).first()
        )
        return user_session
            
class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """

    __tablename__ = "blacklist_tokens"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return "<id: token: {}".format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False
