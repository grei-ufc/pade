FROM python:3.7

MAINTAINER Pade Production <lucassmelo@dee.ufc.br>

LABEL Description="Framework for multiagent systems development in Python. This dockerfile builds a pade production environment."

ENV  FLASK_ENV=production 
ENV  FLASK_DEBUG=0

RUN apt-get update && apt-get install -y python-pip python-dev build-essential python-pyside python-qt4reactor

COPY . /app
WORKDIR /app
RUN python setup.py install

EXPOSE 5000/tcp

CMD sleep infinity
