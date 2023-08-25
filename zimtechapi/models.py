from datetime import datetime, timedelta
import sqlalchemy as sa
from flask import current_app
from zimtechapi.utils.crypt import AESCipher
from flask_bcrypt import Bcrypt
from . import db

bcrypt = Bcrypt()

class WebAppUserWhiteList(db.Model):
    """Allowable usernames ref table"""

    __tablename__ = "WEB_APP_USER_WHITE_LIST"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    email = sa.Column(sa.String(255), unique=True, nullable=False)

    def __init__(self, email):
        self.email = email


class WebAppUser(db.Model):
    """User Model for storing user related details"""

    __tablename__ = "WEB_APP_USER"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    username = sa.Column(sa.String(255), unique=True, nullable=False)
    email = sa.Column(sa.String(255), unique=True, nullable=False)
    password = sa.Column(sa.String(255), nullable=False)
    registered_on = sa.Column(sa.DateTime, nullable=False)
    admin = sa.Column(sa.Boolean, nullable=False, default=False)
    verified = sa.Column(sa.Boolean, nullable=False, default=False)

    def __init__(self, username, email, password, admin=False):
        u = db.session.execute(
            sa.select(WebAppUserWhiteList).filter_by(email=email)
        ).scalar_one()

        if not u.id:
            raise Exception("Email not allowed.")

        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, current_app.config.get("BCRYPT_LOG_ROUNDS")
        ).decode()
        self.registered_on = datetime.now()
        self.admin = admin
        self.verified = False


class WebAppUserSession(db.Model):
    """Web App User Session Model for storing user sessions"""

    __tablename__ = "WEB_APP_USER_SESSION"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(WebAppUser.id), nullable=False)
    session_start_datetime = sa.Column(sa.DateTime, nullable=False)
    session_token = sa.Column(sa.String(255), unique=True, nullable=False)
    session_token_expiration_datetime = sa.Column(sa.DateTime, nullable=False)
    session_token_disabled = sa.Column(sa.Boolean, nullable=False)

    def __init__(self, email, session_length_mins):
        user = db.session.execute(
            sa.select(WebAppUser).filter_by(email=email)
        ).scalar_one()
        self.user_id = user.id
        now = datetime.now()
        cipher = AESCipher(current_app.config.get("SECRET_KEY"))
        self.session_start_datetime = now
        session_token = cipher.encrypt(f"{user.email}{now}").decode()
        self.session_token = session_token
        self.session_token_expiration_datetime = now + timedelta(
            minutes=session_length_mins
        )
        self.session_token_disabled = False

    @staticmethod
    def get_user(session_token: str) -> WebAppUser:
        user_session = WebAppUserSession.query.where(
            WebAppUserSession.session_token == session_token
        ).first()
        if (
            user_session.session_token_expiration_datetime > datetime.now()
            and not user_session.session_token_disabled
        ):
            return WebAppUser.query.where(WebAppUser.id == user_session.user_id).first()
        else:
            return None

    @staticmethod
    def get_active_user_session(session_token: str) -> "WebAppUserSession":
        user_session = WebAppUserSession.query.where(
            WebAppUserSession.session_token == session_token
        ).first()
        if (
            user_session.session_token_expiration_datetime > datetime.now()
            and not user_session.session_token_disabled
        ):
            return user_session
        else:
            return None


class WebAppUserCSRFSession(db.Model):
    """Web App User CSRF Session Model for storing user csrf token sessions"""

    __tablename__ = "WEB_APP_USER_CSRF_SESSION"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(WebAppUser.id), nullable=False)
    session_start_datetime = sa.Column(sa.DateTime, nullable=False)
    csrf_token = sa.Column(sa.String(255), unique=True, nullable=False)
    csrf_token_expiration_datetime = sa.Column(sa.DateTime, nullable=False)
    csrf_token_disabled = sa.Column(sa.Boolean, nullable=False)

    def __init__(self, email, session_length_mins):
        user = db.session.execute(
            sa.select(WebAppUser).filter_by(email=email)
        ).scalar_one()
        self.user_id = user.id
        now = datetime.now()
        self.csrf_token_expiration_datetime = now + timedelta(
            minutes=session_length_mins
        )
        cipher = AESCipher(current_app.config.get("SECRET_KEY"))
        csrf_token = cipher.encrypt(f"{user.email}{now}").decode()
        self.csrf_token = csrf_token
        self.session_start_datetime = now
        self.csrf_token_disabled = False

    @staticmethod
    def is_session_active(email):
        user_session = WebAppUserCSRFSession.get_active_user_csrf_session(email)
        if user_session:
            if datetime.now() > user_session.csrf_token_expiration_datetime:
                return False
            else:
                return True
        else:
            return False

    @staticmethod
    def get_active_user_csrf_session(email: str) -> "WebAppUserCSRFSession":
        user = WebAppUser.query.where(WebAppUser.email == email).first()

        user_session = (
            WebAppUserCSRFSession.query.where(
                WebAppUserCSRFSession.user_id == user.id,
                WebAppUserCSRFSession.csrf_token_disabled == False,
            )
            .order_by(WebAppUserCSRFSession.session_start_datetime.desc())
            .first()
        )
        return user_session
