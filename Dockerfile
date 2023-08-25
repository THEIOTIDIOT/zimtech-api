FROM python:3.11

RUN useradd api

WORKDIR /home/api

COPY requirements.txt ./
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt

COPY pyproject.toml config.ini logger_config.yml boot.sh ./
COPY zimtechapi zimtechapi
COPY migrations migrations
RUN chmod +x boot.sh


RUN pip install -e ./
RUN chown -R api ./

USER api
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]