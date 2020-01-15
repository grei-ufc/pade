import os
import datetime
import requests
import json
import pagan
from requests.exceptions import Timeout
from flask import Flask
from flask import request, render_template, flash, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin, current_user
from flask_wtf import FlaskForm
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_login import UserMixin

from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators
from wtforms.validators import Required, Email, Length

from werkzeug.security import generate_password_hash, check_password_hash

basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)

# Configuracoes do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


# configuracao para utilizacao de chave de seguranca
# em formularios submetidos pelo metodo POST
app.config['SECRET_KEY'] = 'h5xzTxz2ksytu8GJjei37KHI8t0unJKN7EQ8KOPU3Khkjhkjguv'

# configuracao para utilizacao offline do Bootstrap
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

# configuracao do sistema de login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'


db = SQLAlchemy(app)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

bootstrap = Bootstrap(app)


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
    role = db.Column(db.String(32))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
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
    receivers = db.Column(db.String)
    content = db.Column(db.String)
    ontology = db.Column(db.String)
    language = db.Column(db.String)

    def __repr__(self):
        return 'Message %s' % self.id


class RemoteSession(db.Model):
    __tablename__ = 'remote_sessions'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String)
    content = db.Column(db.String)
    last_updated = db.Column(db.DateTime)

    def __repr__(self):
        return 'Ip address %s' % self.ip

    def __init__(self, ip, content, time):
        self.ip = ip
        self.content = content
        self.last_updated = time


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Create')


@app.before_first_request
def create_database():
    db.create_all()
    print('[Flask-Server] >>> Database created.')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/set_admin', methods=['GET', 'POST'])
def set_admin():
    current = current_user
    if current.role == 'Guest':
        flash(u'You dont have permission to do this, send a email to one of the Admins asking to change your role', 'warning')
        users = User.query.all()
        return render_template('manage_users.html', users=users)

    userId = request.form.get('user')
    user = User.query.filter_by(id=userId).first()
    user.role = 'Admin'
    users = User.query.all()
    return render_template('manage_users.html', users=users)


@app.route('/remove_user', methods=['GET', 'POST'])
def remove_user():
    current = current_user
    userId = request.form.get('user')
    user = User.query.filter_by(id=userId).first()

    if user.id == current.id:
        db.session.delete(user)
        flash(u'You removed yourself', 'info')
        logout_user()
        return redirect(url_for('login'))

    if current.role == 'Guest':
        flash(u'You must be Admin to remove any user that is not yourself', 'danger')
        users = User.query.all()
        return render_template('manage_users.html', users=users)

    db.session.delete(user)
    flash(u'User removed sucefully', 'success')
    users = User.query.all()
    return render_template('manage_users.html', users=users)


# If there are already users, they all will have Admin roles
@app.before_first_request
def check_user_roles():
    print("[Flask-Server] >>> Setting Admin roles to existing users")
    users = User.query.all()
    for u in users:
        if u.role is None:
            u.role = 'Admin'


@app.route('/user/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)

    if request.method == 'POST' and form.validate():
        # checking if there are users in the database
        results = User.query.all()

        # if any user was found the user being registered will receive 'Guest' role
        if results is not None:
            user = User(username=form.username.data,
                        email=form.email.data, password=form.password.data, role='Guest')
        # if no user was found, then the first one must be the Admin
        else:
            user = User(username=form.username.data,
                        email=form.email.data, password=form.password.data, role='Admin')

        db.session.add(user)
        flash(u'Thanks for registering', 'success')
        return redirect(url_for('login'))
    return render_template('register_users.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    countUsers = User.query.count()
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for('index'))
        flash(u'Invalid username or password.', 'danger')
        return render_template('login.html', form=form)
    else:
        user = request.form.get('username', type=str)
        password = request.form.get('password', type=str)
        remember = request.form.get('remember', type=bool)
        user = User.query.filter_by(username=user).first()
        if user is not None and user.verify_password(password):
            login_user(user, remember)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', form=form, countUsers=countUsers)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash(u'You have been logged out', 'warning')
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    sessions = Session.query.all()
    rsessions = RemoteSession.query.all()
    return render_template('index.html', sessions=sessions, rsessions=rsessions)


@app.route('/messagesTable')
def messagesTable():
    messages = Message.query.order_by(Message.date.desc()).limit(5)
    return render_template('messagesTable.html', messages=messages)


@app.route('/messagesList', methods=['GET'])
def messagesList():
    messages = Message.query.all()
    return render_template('messagesList.html', messages=messages)


@app.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    current = current_user
    users = User.query.all()
    return render_template('manage_users.html', users=users, current=current)


@app.route('/session/<session_id>')
@login_required
def session_page(session_id):
    generate_agent_avatars()
    session = Session.query.filter_by(id=session_id).first()
    agents = session.agents
    return render_template('agentes.html', session=session, agents=agents)


@app.route('/rsession/<rsession_id>')
@login_required
def rsession_pade(rsession_id):
    res = RemoteSession.query.filter_by(id=rsession_id).first()
    data = json.loads(res.content)
    return render_template('remote_sessions.html', data=data)


@app.route('/session/agent/<agent_id>')
@login_required
def agent_messages(agent_id):
    agent = AgentModel.query.filter_by(id=agent_id).first()
    messages = agent.messages
    return render_template('agent_messages.html', messages=messages, agent=agent)


@app.route('/session/agents', methods=['POST'])
def manageAgent():
    agent = request.form.get('stop')
    if agent:
        agent = AgentModel.query.filter_by(id=agent).first()
        agent.state = 'Paused'
        session = agent.session
        agents = session.agents
        return render_template('agentes.html', session=session, agents=agents)

    agent = request.form.get('start')
    if agent:
        agent = AgentModel.query.filter_by(id=agent).first()
        agent.state = 'Active'
        session = agent.session
        agents = session.agents
        return render_template('agentes.html', session=session, agents=agents)

    agent = request.form.get('kill')
    if agent:
        agent = AgentModel.query.filter_by(id=agent).first()
        agent.state = 'Dead'
        session = agent.session
        agents = session.agents
        return render_template('agentes.html', session=session, agents=agents)

    sessions = Session.query.all()
    return render_template('index.html', sessions=sessions)


@app.route('/session/agent/message/<message_id>')
@login_required
def message_page(message_id):
    message = Message.query.filter_by(id=message_id).first()
    return render_template('message.html', message=message)


@app.route('/sessions', methods=['GET', 'POST'])
@login_required
def manage_sessions():
    return render_template('sessions.html')


@app.route('/remote_sessions', methods=['GET'])
def get_sessions():
    data = []

    # List to store agents over the loop
    agents = []
    messages = []
    sessions = Session.query.all()

    for session in sessions:
        data = {'Session Name': session.name,
                'Session ID': session.id,
                'Session Date': session.date,
                'Session State': session.state,
                'Agents': [],
                'Messages': []
                }

        for agent in session.agents:
            data_agents = {'Agent ID': agent.id,
                           'Session Agent ID': agent.session.id,
                           'Agent Name': agent.name,
                           'Agent Date': agent.date,
                           'Agent State': agent.state,
                           }

            for m in agent.messages:
                data_messages = {'Message ID': m.id,
                                 'Agent Message ID': m.agent_id,
                                 'Conversation ID': m.conversation_id,
                                 'Message Date': m.date,
                                 'Message Performative': m.performative,
                                 'Protocol': m.protocol,
                                 'Sender': m.sender,
                                 'Receivers': m.receivers,
                                 'Content': m.content,
                                 'Ontology': m.ontology,
                                 'Language': m.language,
                                 }

                messages.append(data_messages)

            data['Messages'] = messages
            agents.append(data_agents)

        data['Agents'] = agents

    return jsonify(data)


@app.route('/send_request', methods=['GET', 'POST'])
def send_request():
    if request.method == 'GET':
        return render_template('sessions.html')
    if request.method == 'POST':
        host = request.form.get('host_ip')

        # Checking if the session hasn't been added already
        res = RemoteSession.query.filter_by(ip=host).first()

        if res:
            flash(u'This session has already been added, you can see it on the home page', 'warning')
            return render_template('sessions.html')
        elif host == '0.0.0.0':
            flash(u'You cannot add a localhost session', 'warning')
            return render_template('sessions.html')
        else:
            try:
                response = requests.get('http://' + host + ':5000/remote_sessions', timeout=(10, 20))

                if response:
                    data = response.json()
                    time = datetime.datetime.now()
                    save_remote_session(host, response.content, time)
                    flash(u'A remote PADE instance was found and saved automatically! :)', 'success')
                    return render_template('remote_sessions.html', data=data)

                else:
                    flash(u'Sorry, no PADE session was found in this IP, please check again', 'danger')
                    return render_template('sessions.html')
            except Timeout:
                flash(u'Sorry, your request timed out, please check again', 'danger')
                return render_template('sessions.html')


def save_remote_session(ip, content, time):
    s = RemoteSession(ip, content, time)
    db.session.add(s)
    db.session.flush()
    db.session.commit()


@app.route('/diagrams', methods=['GET', 'POST'])
@login_required
def diagrams():
    return render_template('diagrams.html')


@app.route('/messages_diagram', methods=['GET'])
def messages_diagram():
    data = Message.query.order_by(Message.date)
    data_diagram = ''

    for msg in data:
        content = msg.content
        sender = msg.sender.split("@")[0]
        receivers = msg.receivers
        performative = msg.performative

        # Limiting the size of the message to be displayed
        if len(content) > 50:
            content = "Content is too big to be displayed :( \n\n Please adjust your message."

        data_diagram += sender + '-->' + receivers + ': ' + performative + '\n'
        data_diagram += sender + '->' + receivers + ': ' + content + '\n'

    return render_template('messagesDiagrams.html', messages=data_diagram)


@app.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    data = Message.query.all()
    senders = []
    performatives = []

    # This for loop its used to get all the senders and performatives from the messages being sent,
    # so it can be used in the filters
    for message in data:
        if message.sender not in senders[:]:
            senders.append(message.sender)

        if message.performative not in performatives[:]:
            performatives.append(message.performative)

    if request.method == 'GET':
        return render_template('messages.html', messages=data, senders=senders, performatives=performatives)

    if request.method == 'POST':

        data = []

        ###############################
        # Capturing values from input #
        ###############################
        selected_sender = request.form.get('sender')
        selected_performative = request.form.get('performative')
        content = request.form.get('content')
        time_start = request.form.get('timeStart')
        time_stop = request.form.get('timeStop')

        if content:
            data = Message.query.filter(Message.content.contains(content))

        if selected_performative:
            data = Message.query.filter(Message.performative == selected_performative)

        if selected_sender:
            data = Message.query.filter(Message.sender == selected_sender)

        if time_start:
            start = time_start.replace("T", " ") + ":00.000000"
            stop = time_stop.replace("T", " ") + ":59.999999"
            data = Message.query.filter(Message.date > start).filter(Message.date < stop)

        return render_template('messagesFiltered.html', messages=data, senders=senders, performatives=performatives)


def generate_agent_avatars():
    # Defining the directory to save the avatars images
    path = os.path.abspath(os.path.dirname(__file__)) + '/static'

    # Checking for existing avatars in directory
    files = os.listdir(path)

    # Querying agents
    agents = AgentModel.query.all()

    for a in agents:
        # Converting the agent object to string (agent name)
        name = str(a)
        name = name[6:-17]

        if any(name in s for s in files):
            # If any avatar image with the agent name already exists
            # then nothing is necessary
            pass
        else:
            # If no avatar image with the agent name was found
            # then one is created
            img = pagan.Avatar(name, pagan.SHA512)
            img.save(path, name)

@app.route('/post',  methods=['POST', 'GET'])
def my_post():
    if request.method == 'GET':
        return basedir
    else:
        return 'Hello ' + str(request.form['name'])


def run_server(secure):
    if secure:
        login_manager._login_disabled = False
    else:
        login_manager._login_disabled = True

    app.run(host='0.0.0.0', port=5000, debug=None)


if __name__ == '__main__':
    manager.run()
    run_server(secure)
