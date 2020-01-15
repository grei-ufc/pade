FROM python:3.7

MAINTAINER Pade Development <lucassmelo@dee.ufc.br>

LABEL Description="Framework for multiagent systems development in Python. This dockerfile builds a pade development environment."

ENV  FLASK_ENV=development 
ENV  FLASK_DEBUG=1

RUN apt-get update && apt-get install -y python-pip python-dev build-essential python-pyside python-qt4reactor

COPY . /app
WORKDIR /app
RUN python setup.py install

CMD sleep infinity
