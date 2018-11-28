import os
from flask import Flask
from flask import request, render_template, flash, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Email, Length, ValidationError, DataRequired, EqualTo
from werkzeug.urls import url_parse

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug import generate_password_hash, check_password_hash


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Configuracoes do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# configiracao para utilizacao de chave de seguranca
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

    # @property
    # def password(self):
    #     raise AttributeError('password is not a readable attribute!')

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

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('login'))

@app.route('/')
@app.route('/index')
@login_required
def index():
    sessions = Session.query.all()
    return render_template('index.html', sessions=sessions)

@app.route('/session/<session_id>')
@login_required
def session_page(session_id):
    session = Session.query.filter_by(id=session_id).first()
    agents = session.agents
    return render_template('agentes.html', session=session, agents=agents)

@app.route('/session/agent/<agent_id>')
@login_required
def agent_page(agent_id):
    agent = AgentModel.query.filter_by(id=agent_id).first()
    messages = agent.messages
    return render_template('messages.html', messages=messages, agent=agent)

@app.route('/session/agent/message/<message_id>')
@login_required
def message_page(message_id):
    message = Message.query.filter_by(id=message_id).first()
    return render_template('message.html', message=message)

@app.route('/diagrams')
@login_required
def diagrams():
    messages = Message.query.order_by(Message.date).all()
    _messages = list()
    msgs_id = list()

    for msg in messages:
        if msg.message_id in msgs_id:
            messages.remove(msg)
            continue
        msgs_id.append(msg.message_id)

    messages_diagram = ''
    for msg in messages:
        for receiver in msg.receivers:
            messages_diagram += str(msg.sender) + '->' + str(receiver) + ': ' + str(msg.performative) + '\n'
    return render_template('diagrams.html', messages=messages_diagram)

@app.route('/post',  methods=['POST', 'GET'])
def my_post():
    if request.method == 'GET':
        return basedir
    else:
        return 'Hello ' + str(request.form['name'])



@app.before_first_request
def create_database():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def run_server():
    app.run(host='0.0.0.0', port=5000, debug=None)

if __name__ == '__main__':
    run_server()
