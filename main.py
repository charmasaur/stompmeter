from flask import Flask, redirect, request, render_template, url_for
from google.appengine.api import users
import base64
import datetime
import hashlib
import json

import user_store

app = Flask(__name__)

@app.route('/', methods=['GET'])
def welcome():
    user = users.get_current_user()
    if user and signed_up(user):
        return redirect('dashboard')

    return render_template("welcome.html")

@app.route('/signup', methods=['GET'])
def signup():
    user = users.get_current_user()
    default_nick = ""
    if signed_up(user):
        default_nick = user_store.get_nick(user)

    return render_template(
            "signup.html",
            email=user.email(),
            default_nick=default_nick)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    user = users.get_current_user()
    if not signed_up(user):
        return redirect('/')

    return render_template(
            "dashboard.html",
            nick=user_store.get_nick(user))

@app.route('/record', methods=['GET'])
def record():
    user = users.get_current_user()
    if not signed_up(user):
            return redirect('/')

    return render_template(
            "record.html",
            nick=user_store.get_nick(user))

@app.route('/set_record', methods=['POST'])
def set_record():
    user = users.get_current_user()
    if not signed_up(user):
            return redirect('/')
    raw_data = request.form.to_dict()

    # Need a valid date for this to work, so check that first.
    date_string = raw_data.get("date", "")
    if date_string == "":
        return render_template("set_record_fail.html", msg="No date")
    date_elements = [int(x) for x in date_string.split("-")]
    date = datetime.date(date_elements[0], date_elements[1], date_elements[2])

    # We've got a valid date, so first try to save the raw data.
    if not user_store.save_raw_data(user, raw_data):
        return render_template("set_record_fail.html", msg="Raw data failed")

    return render_template("set_record.html")

@app.route('/set_nick', methods=['GET'])
def set_nick():
    user = users.get_current_user()
    nick = request.args.get("nick")
    if not nick:
        return redirect('signup')

    user_store.set_nick(user, nick)
    return redirect('dashboard')

def signed_up(user):
    if user_store.get_nick(user):
        return True
    return False
