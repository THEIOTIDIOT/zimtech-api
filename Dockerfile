FROM python:3.11

RUN useradd api

WORKDIR /home/api

COPY requirements.txt ./
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY pyproject.toml config.ini logger_config.yml boot.sh ./
COPY zimtechapi zimtechapi
COPY migrations migrations
RUN chmod +x boot.sh


RUN pip install -e ./zimtechapi
RUN chown -R zimtechapi:zimtechapi ./

USER api
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]