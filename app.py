from flask import Flask, render_template
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'funy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite///data.db'

@login_manager.user_loader
def load_user(user):
    return User.get(user)

class User(db.Model, UserMixin):
    # a
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()
