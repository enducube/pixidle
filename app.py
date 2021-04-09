"""
pixidle by enducube/Jack Milner
"""
## Imports
from flask import Flask, render_template, redirect
# Login and CRUD interaction with database
from flask_login import LoginManager, UserMixin, login_user
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


# Form classes (yeah pretty funny I know)

class LoginForm(FlaskForm):
    username = StringField(DataRequired())
    password = PasswordField(DataRequired())


## Routes and other stuff

# flask routes

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=('GET', 'POST'))
def register():
    form = LoginForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/")
    return render_template("register.html",form=form)

@app.route("/login", methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, password=form.password.data).first()
        if user:
            login_user(user)
    return render_template("login.html",form=form)


# Socket.IO routes
@socketio.on("register")
def socket_register(json):
    data = dict(json)
    print(data['username'])
    print(data['password'])
    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return redirect("/")



if __name__ == "__main__":
    print("bar")
    socketio.run(app)
