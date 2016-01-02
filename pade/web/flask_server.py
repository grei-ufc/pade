import os
from flask import Flask
from flask import request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Configuracoes do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

bootstrap = Bootstrap(app)

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    date = db.Column(db.DateTime)
    state = db.Column(db.String(64))
    agents = db.relationship('Agent', backref='session')

    def __repr__(self):
        return "Session %s" % self.name


class Agent(db.Model):

    __tablename__ = 'agents'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    name = db.Column(db.String(64), unique=True)
    date = db.Column(db.DateTime)
    state = db.Column(db.String(64))
    messages = db.relationship('Message', backref='agent')
    def __repr__(self):
        return "Agent %s" % self.name


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
        return "Message %s" % self.id

@app.before_first_request
def create_database():
    db.create_all()
    print '[flask-server] >>> Database created.'

@app.route('/')
def index():
    sessions = Session.query.all()
    return render_template('index.html', sessions=sessions)

@app.route('/session/<session_id>')
def session_page(session_id):
    session = Session.query.filter_by(id=session_id).all()[0]
    agents = session.agents
    return render_template('agentes.html', session=session.name, agents=agents)

@app.route('/session/agent/<agent_id>')
def agent_page(agent_id):
    agent = Agent.query.filter_by(id=agent_id).all()[0]
    messages = agent.messages
    return render_template('messages.html', messages=messages)

@app.route('/session/agent/message/<message_id>')
def message_page(message_id):
    message = Message.query.filter_by(id=message_id).all()[0]
    return render_template('message.html', message=message)

@app.route('/diagrams')
def diagrams():
    messages = Message.query.order_by(Message.date).all()
    _messages = list()
    msgs_id = list()

    for msg in messages:
        if msg.message_id in msgs_id:
            messages.remove(msg)
            continue
        msgs_id.append(msg.message_id)

    return render_template('diagrams.html', messages=messages)

@app.route('/post',  methods=['POST', 'GET'])
def my_post():
    if request.method == 'GET':
        return basedir
    else:
        return 'Hello ' + str(request.form['name'])

def run_server():
    app.run(host='0.0.0.0', port=5000, debug=None)

if __name__ == '__main__':
    run_server()
