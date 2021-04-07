from flask import Flask, render_template
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO
import eventlet

# Init app

app = Flask(__name__)
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.init_app(app)


app.config['SECRET_KEY'] = 'funy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite///data.db'

socketio = SocketIO(app)

@login_manager.user_loader
def load_user(user):
    return User.query.get(user)

# Classes and such

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

class LoginForm(FlaskForm):
    username = StringField()
    password = StringField()


# Routes and other stuff

@app.route("/")
def index():
    form = LoginForm()
    return render_template("index.html",form=form)

@app.route("/login", methods=('GET', 'POST'))
def login():
    form = LoginForm()


# Socket.IO routes
@socketio.on("login")
def socketlogin(json):
    data = dict(json)
    print(data['username'])
    print(data['password'])



if __name__ == "__main__":
    print("bar")
    socketio.run(app)
