## Imports
from flask import Flask, render_template, redirect, url_for
# Login and CRUD interaction with database
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
# Form modules
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.validators import InputRequired, DataRequired
# Werkzeug features
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
# Socket.IO and eventlet
from flask_socketio import SocketIO
from flaskext.markdown import Markdown
import gevent
from flaskext.markdown import Markdown

## Init app

connected_users = []

app = Flask(__name__)
app.config['SECRET_KEY'] = 'funy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["UPLOAD_FOLDER"] = "/static/profile"

# Setup extra stuff for the app (sqlalchemy, flask_login, socketio)

db = SQLAlchemy()
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")
markdown = Markdown(app)

from app import routes




