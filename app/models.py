from app import db, FlaskForm, UserMixin, generate_password_hash, check_password_hash, StringField, PasswordField, FileField, InputRequired, DataRequired, ColorField
## Classes and such

class User(db.Model, UserMixin):
    # The user class
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    img = db.Column(db.String, default="normal.png")
    colour = db.Column(db.String, default="ffffff")

    def set_password(self, password):
        self.password = generate_password_hash(password,method="sha256")
    def check_password(self, password):
        return check_password_hash(self.password, password)

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
    file = FileField()

class UploadForm(FlaskForm):
    file = FileField(DataRequired())

class CustomiseForm(FlaskForm):
    file = FileField()
    colour = ColorField()