from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from blog.config import postgres_connection

engine = create_engine(postgres_connection)
db_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)
Base = declarative_base()
Base.query = db_session.query_property()
metadata = None

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from datetime import datetime
    import sqlalchemy as sa
    from flask import current_app
    from blog.utils.utils import AESCipher
    from flask_sqlalchemy import SQLAlchemy
    from flask_bcrypt import Bcrypt
    Base.metadata.create_all(bind=engine)