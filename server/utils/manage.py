"""
python -m venv .venv
.venv/Scripts/Activate.ps1
set FLASK_ENV=development
pip freeze > requirements.txt
set FLASK_APP=app.py  
export FLASK_APP=app.py
flask --app project.server db init
flask --app project.server db migrate
flask --app project.server db upgrade
flask --app project.server --debug run

"""
# TODO: Create a management utility for dealing with testing and database initialization/migration/upgrade routines
