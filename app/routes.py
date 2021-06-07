from app import (app, socketio, login_required, 
 models, current_user, redirect, render_template,
 logout_user, login_user, login_manager, db, markdown, secure_filename)

from app.models import User, Message, Channel, LoginForm, MessageForm, UploadForm

#### Routes and other stuff

@login_manager.user_loader
def load_user(user):
    return User.query.get(user)

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

@app.route("/accountsettings")
@login_required
def settings():
    form = UploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        form.file.data.save("static/profile/")
    return render_template("settings.html")

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
    