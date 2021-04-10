"""
pixidle by enducube/Jack Milner
"""
## Imports
from flask import Flask, render_template, redirect, url_for
# Login and CRUD interaction with database
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
# Form modules
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.validators import DataRequired
# Werkzeug features
from werkzeug.security import generate_password_hash, check_password_hash
# Socket.IO and eventlet
from flask_socketio import SocketIO
import eventlet

## Init app

app = Flask(__name__)
app.config['SECRET_KEY'] = 'funy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup extra stuff for the app (sqlalchemy, flask_login, socketio)

db = SQLAlchemy()
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
socketio = SocketIO(app)

@login_manager.user_loader
def load_user(user):
    return User.query.get(user)

## Classes and such

class User(db.Model, UserMixin):
    # The user class
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)

    def set_password(self, password):
        self.password = generate_password_hash(password,method="sha256")
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Message(db.Model):
    __tablename__ = "message"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.Integer)
    channel_id = db.Column(db.Integer)
    message = db.Column(db.Text)

class Channel(db.Model):
    __tablename__ = "channel"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    owner_id = db.Column(db.Integer)

# Form classes (yeah pretty funny I know)

class LoginForm(FlaskForm):
    username = StringField(DataRequired())
    password = PasswordField(DataRequired())

class MessageForm(FlaskForm):
    message = StringField(DataRequired())

#### Routes and other stuff

## flask routes

@app.context_processor
def context():
    def get_user_from_id(id):
        found_user = User.query.filter_by(id=id).first()
        return found_user.username
    return dict(get_user_from_id=get_user_from_id)

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect("/home/general")
    return render_template("index.html")

# user stuff routes or something

@app.route("/register", methods=('GET', 'POST'))
def register():
    form = LoginForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, password=form.password.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user)
        return redirect("/home/general")
    return render_template("register.html",form=form)

@app.route("/login", methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/home/general")
    return render_template("login.html",form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

################ The meat of the application (where the chatting will occur) ################

@app.route("/home/<channel_name>")
@login_required
def home(channel_name):
    msg_form = MessageForm()
    channel = Channel.query.filter_by(name=channel_name).first()

    return render_template("home.html",form=msg_form,channel_id=channel.id,channel_name=channel_name)

@app.route("/channel/<channel_id>")
def channel_render(channel_id):
    messages = list(Message.query.filter_by(channel_id=channel_id))
    print(messages)
    return render_template("channel.html",messages=messages)

## Socket.IO routes

@socketio.on("message")
def socket_message(json):
    data=dict(json)
    print(data)
    msg = Message(message=data['message'], user_id=data['user_id'], channel_id=data['channel_id'])
    db.session.add(msg)
    db.session.commit()
    socketio.emit("msg",broadcast=True)
@socketio.on("connect")
def connection():
    socketio.emit("msg")


if __name__ == "__main__":
    print("bar")
    socketio.run(app)
