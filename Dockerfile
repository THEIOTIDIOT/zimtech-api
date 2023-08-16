FROM python:3.11

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY pyproject.toml ./
COPY zimtechapi ./
COPY config.ini ./
COPY logger_config.yml ./
RUN pip install -e ./zimtechapi

COPY . .

CMD [ "python -m zimtechapi.database.init_db()", "gunicorn -w 4 'zimtechapi.create_app()'" ]