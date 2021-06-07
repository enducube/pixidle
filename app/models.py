from app import db, FlaskForm, UserMixin, generate_password_hash, check_password_hash, StringField, PasswordField, FileField, InputRequired, DataRequired
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
    username = StringField(InputRequired())
    password = PasswordField(InputRequired())

class MessageForm(FlaskForm):
    message = StringField(InputRequired())

class UploadForm(FlaskForm):
    file = FileField(DataRequired())