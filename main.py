from flask import Flask, redirect, request, render_template, url_for
from google.appengine.api import users
import base64
import datetime
import hashlib
import json

import points_calculator
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
    recents = []
    recent_stuffs = user_store.get_recent_points(user, 7)
    if recent_stuffs:
        for date, points in recent_stuffs:
            recents.append({
                'date':str(date),
                'points':str(points)
                })

    return render_template(
            "dashboard.html",
            nick=user_store.get_nick(user),
            recents=recents)

@app.route('/record', methods=['GET'])
def record():
    user = users.get_current_user()
    if not signed_up(user):
            return redirect('/')

    return render_template(
            "record.html",
            nick=user_store.get_nick(user))

@app.route('/login', methods=['GET'])
def login():
    return redirect(users.CreateLoginURL('/dashboard'))

@app.route('/logout', methods=['GET'])
def logout():
    return redirect(users.CreateLogoutURL('/'))

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

    # That's all good, so now calculate the points and save those.
    standing = get_float_or_zero(raw_data, "standing")
    walking = get_float_or_zero(raw_data, "walking")
    running = get_float_or_zero(raw_data, "running")
    cycling = get_float_or_zero(raw_data, "cycling")
    swimming = get_float_or_zero(raw_data, "swimming")
    stretching = get_float_or_zero(raw_data, "stretching")
    points = points_calculator.calculate(
            standing, walking, running, cycling, swimming, stretching)

    success, total_daily_points = user_store.save_points(user, date, points)
    if not success:
        return render_template("set_record_fail.html",
                msg="Points failed. This really shouldn't have happened.")

    return render_template("set_record.html",
            msg="Today you've earned " + str(total_daily_points) +
                    " points, woah!")

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

def get_float_or_zero(raw_data, key):
    res = raw_data.get(key, "")
    if res == "":
        return 0
    return float(res)
