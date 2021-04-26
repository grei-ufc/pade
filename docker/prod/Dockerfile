FROM python:3.7

LABEL MAINTAINER="Pade Production <lucassmelo@dee.ufc.br>"

LABEL Description="Framework for multiagent systems development in Python. This dockerfile builds a pade production environment."

ENV  FLASK_ENV=production 
ENV  FLASK_DEBUG=0

RUN apt-get update && apt-get install -y python-pip python-dev 
RUN apt-get install -y build-essential python-qt4reactor 
# RUN apt-get install -y python-pyside
RUN pip3 install -U PySide2
COPY . /app
WORKDIR /app
RUN python setup.py install

EXPOSE 5000/tcp

CMD sleep infinity
