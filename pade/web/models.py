from datetime import datetime
from .flask_server import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    date = db.Column(db.DateTime)
    state = db.Column(db.String(64))
    agents = db.relationship('AgentModel', backref='session')
    users = db.relationship('User', backref='session')

    def __repr__(self):
        return "Session %s" % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return 'Username: %s' % self.username


class AgentModel(db.Model):
    __tablename__ = 'agents'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    name = db.Column(db.String(64), unique=True)
    date = db.Column(db.DateTime)
    state = db.Column(db.String(64))
    messages = db.relationship('Message', backref='agent')
    def __repr__(self):
        return 'Agent %s' % self.name


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'))
    conversation_id = db.Column(db.String(64))
    message_id = db.Column(db.String(64))
    date = db.Column(db.DateTime)
    performative = db.Column(db.String(64))
    protocol = db.Column(db.String(64))
    sender = db.Column(db.String(64))
    receivers = db.Column(db.PickleType)
    content = db.Column(db.String)
    ontology = db.Column(db.String)
    language = db.Column(db.String)

    def __repr__(self):
        return 'Message %s' % self.id