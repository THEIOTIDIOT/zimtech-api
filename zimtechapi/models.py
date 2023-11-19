from flask_security.models import fsqla_v2 as fsqla
from flask_security import SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    String,
    Text,
    UnicodeText,
    Integer,
    ForeignKey,
    DateTime,
    Boolean,
)
import typing as t

db = SQLAlchemy()

# Define models
fsqla.FsModels.set_db_info(db)


class Role(db.Model, fsqla.FsRoleMixin):
    pass


class User(db.Model, fsqla.FsUserMixin):
    # Because we set "us_phone_number" as a USER_IDENTITY - it must be unique
    us_phone_number = Column(String(128), unique=True, nullable=True)
    blogs: db.Mapped[t.List["Blog"]] = db.relationship(
        "Blog", back_populates="user", lazy="dynamic", cascade_backrefs=False
    )


class Blog(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user: db.Mapped["User"] = db.relationship(
        "User", back_populates="blogs", cascade_backrefs=False
    )
    created_datetime = Column(DateTime(), nullable=False)
    updated_datetime = Column(DateTime(), nullable=True)
    title = Column(String(255))
    body = Column(UnicodeText)
    published = Column(Boolean, nullable=False)


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)