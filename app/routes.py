from app import (app, socketio, login_required, 
 models, current_user, redirect, render_template,
 logout_user, login_user, login_manager, db, markdown, secure_filename, url_for, connected_users)

from app.models import User, Channel, LoginForm, MessageForm, UploadForm, CustomiseForm

import os
import json
import re
import uuid

#### Routes and other stuff

@login_manager.user_loader
def load_user(user):
    return User.query.get(user)

## flask routes

@app.context_processor
def context():
    def get_user_from_id(id):
        found_user = User.query.filter_by(id=id).first()
        return found_user
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
        login_user(user) # automatically log in the user
        return redirect("/home/general")
    return render_template("register.html", form=form)

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

@app.route("/accountsettings", methods=('GET', 'POST'))
@login_required
def settings():
    form = CustomiseForm()
    if form.validate_on_submit():
        if form.file.data != None:
            print(form.file.data.filename)
            filename = secure_filename(str(current_user.id)+'.'+form.file.data.filename.rsplit('.',1)[1])
            print(os.getcwd())
            form.file.data.save(os.path.normpath(os.path.join(os.path.dirname(__file__),"static/profile", filename)))
            current_user.img = filename
        if form.colour.data != None:
            print(form.colour.data.hex_l[1:])
            current_user.colour = str(form.colour.data.hex_l[1:])
            print(form.colour.data.hex_l[1:])
        db.session.commit()
    
    return render_template("settings.html", form=form, channel_name="Settings")

################ The meat of the application (where the chatting will occur) ################

@app.route("/home/<channel_name>")
@login_required
def home(channel_name):
    msg_form = MessageForm()
    channel = Channel.query.filter_by(name=channel_name).first()

    return render_template("home.html",form=msg_form,channel_id=channel.id,channel_name=channel_name,connected_users=connected_users)

@app.route("/userlist")
def userlist_render():
    return render_template("userlist.html",connected_users=connected_users)

## Socket.IO routes

@socketio.on("message")
def socket_message(jsondata):
    data = dict(jsondata)
    data['name'] = User.query.filter_by(id=data['user_id']).first().username
    data['img'] = url_for('static', filename='profile/'+ str(current_user.img))
    data['colour'] =  current_user.colour
    #msg = Message(message=data['message'], user_id=data['user_id'], channel_id=data['channel_id'])
    #db.session.add(msg)
    #db.session.commit()
    
    socketio.emit("msg",data,broadcast=True)

@socketio.on("connect")
def connection():
    if (str(current_user.username),url_for('static', filename='profile/'+ str(current_user.img))) not in connected_users:
        connected_users.append( (str(current_user.username),url_for('static', filename='profile/'+ str(current_user.img)), str(current_user.colour)) )
    socketio.emit("msg",{'name': "SERVER", "colour": "FFFFFF", "img": url_for('static', filename='profile/normal.png'), "message": current_user.username+" has connected."})
    socketio.emit("userlist_refresh",broadcast=True)

@socketio.on("disconnect")
def disconnection():
    if (str(current_user.username),url_for('static', filename='profile/'+ str(current_user.img)), str(current_user.colour)) in connected_users:
        connected_users.pop(connected_users.index( (str(current_user.username),url_for('static', filename='profile/'+ str(current_user.img)), str(current_user.colour)) ))
    socketio.emit("msg",{'name': "SERVER", "img": url_for('static', filename='profile/normal.png'), "message": current_user.username+" has disconnected.", "colour": "FFFFFF"})
    socketio.emit("userlist_refresh",broadcast=True)
    