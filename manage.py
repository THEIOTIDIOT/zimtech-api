"""
python -m venv .venv
.venv/Scripts/Activate.ps1
set FLASK_ENV=development
pip freeze > requirements.txt
set FLASK_APP=app.py  
export FLASK_APP=app.py
"""

# import os
# import unittest
# import coverage
# from flask_script import Manager
# from flask_migrate import Migrate
# from server import app
# import logging

# logger = logging.getLogger(__name__)

# COV = coverage.coverage(
#     branch=True,
#     include='server/*',
#     omit=[
#         'tests/*',
#         'server/config.py',
#         'server/*/__init__.py'
#     ]
# )
# COV.start()

# from server import app, db, models


# migrate = Migrate(app, db)
# manager = Manager(app)


# @manager.command
# def test():
#     """Runs the unit tests without test coverage."""
#     tests = unittest.TestLoader().discover('tests', pattern='test*.py')
#     result = unittest.TextTestRunner(verbosity=2).run(tests)
#     if result.wasSuccessful():
#         return 0
#     return 1


# @manager.command
# def cov():
#     """Runs the unit tests with coverage."""
#     tests = unittest.TestLoader().discover('project/tests')
#     result = unittest.TextTestRunner(verbosity=2).run(tests)
#     if result.wasSuccessful():
#         COV.stop()
#         COV.save()
#         print('Coverage Summary:')
#         COV.report()
#         basedir = os.path.abspath(os.path.dirname(__file__))
#         covdir = os.path.join(basedir, 'tmp/coverage')
#         COV.html_report(directory=covdir)
#         print(f'HTML version: file://{covdir}/index.html')
#         COV.erase()
#         return 0
#     return 1

# @manager.command
# def create_db():
#     """Creates the db tables."""
#     db.create_all()


# @manager.command
# def drop_db():
#     """Drops the db tables."""
#     db.drop_all()

# @manager.command
# def init_db():
#     """Initialize local migration folder and migrates models to server.
#     flask --app server db migrate
#     flask --app server db upgrade
#     flask --app server --debug run"""
#     try:
#         os.system("flask --app server db init")
#         os.system("flask --app server db migrate")
#     except Exception as ex:
#         logger.exception(ex)

# @manager.command
# def upgrade_db():
#     """Upgrades database tables"""
#     try:
#         os.system("flask --app server db upgrade")
#     except Exception as ex:
#         logger.exception(ex)

# if __name__ == '__main__':
#     app.run()