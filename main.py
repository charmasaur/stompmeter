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
    today_date = datetime.date.today()
    # if we're on the nth day of the week (n=0 is Monday), the Monday of the
    # week was n days ago...
    week_start_date = today_date - datetime.timedelta(today_date.weekday())
    # ... and the Sunday on which this week will end is 6 days later.
    this_week_end_date = week_start_date + datetime.timedelta(6)
    week_points = 0
    if recent_stuffs:
        for date, points in recent_stuffs:
            recents.append({
                'date':str(date),
                'points':str(points)
                })
            if date >= week_start_date and date < this_week_end_date:
                week_points += points

    this_nick = user_store.get_nick(user)
    scoreboard = user_store.get_scoreboard()
    nicks = []
    weeks = []
    glowsticks = []
    all_week_end_dates = set()
    for (nick, d) in scoreboard:
        nicks.append({"v":nick,"e":nick == this_nick})
        glowsticks.append({"v":0,"e":False})
        all_week_end_dates.update(d.keys())

    for week_end_date in reversed(sorted(all_week_end_dates)):
        # Get the points scored by each user
        points_num = [d.get(week_end_date, 0) for (_, d) in scoreboard]

        # Convert that to strings
        points = [{"v":str(p),"e":False} for p in points_num]

        # Update the total glowsticks, and while we're there set any necessary
        # emphasis on the points
        winning_score = max(points_num)
        for (i, p) in enumerate(points_num):
            if p == winning_score:
                glowsticks[i]["v"] += 1
                points[i].update({"e":True})

        weeks.append({"date":str(week_end_date), "points":points})

    # Set emphasis on the glowsticks
    if len(nicks) > 0:
        winning_glowsticks = max([g["v"] for g in glowsticks])
        for d in glowsticks:
            if d["v"] == winning_glowsticks:
                d["e"] = True

    return render_template(
            "dashboard.html",
            nick=this_nick,
            recents=recents,
            week_end_date=str(this_week_end_date),
            week_points=str(week_points),
            nicks=nicks,
            glowsticks=glowsticks,
            weeks=weeks)

@app.route('/record', methods=['GET'])
def record():
    user = users.get_current_user()
    if not signed_up(user):
            return redirect('/')

    return render_template(
            "record.html",
            nick=user_store.get_nick(user))

@app.route('/admin', methods=['GET'])
def admin():
    return render_template("admin.html")

@app.route('/snapshot_today', methods=['GET'])
def snapshot_today():
    return try_to_do_snapshot(datetime.date.today())

@app.route('/snapshot', methods=['GET'])
def snapshot():
    return try_to_do_snapshot(extract_date(request.args.get("date", "")))

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
    date = extract_date(raw_data.get("date", ""))
    if not date:
        return render_template("set_record_fail.html", msg="No date")

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
            msg="On " + str(date) + " you earned " + str(total_daily_points) +
                    " points, woah!")

@app.route('/set_nick', methods=['GET'])
def set_nick():
    user = users.get_current_user()
    nick = request.args.get("nick")
    if not nick:
        return redirect('signup')

    user_store.set_nick(user, nick)
    return redirect('dashboard')

def try_to_do_snapshot(date):
    if not date:
        return "Snapshot failed: bad date"

    if not date.weekday() == 6:
        return "Snapshot failed: must snapshot a Sunday"

    user_store.snapshot_week_scores(date)
    return "Snapshot succeeded for week: " + str(date)

def extract_date(form_entry):
    if form_entry == "":
        return None
    date_elements = [int(x) for x in form_entry.split("-")]
    return datetime.date(date_elements[0], date_elements[1], date_elements[2])

def signed_up(user):
    if user_store.get_nick(user):
        return True
    return False

def get_float_or_zero(raw_data, key):
    res = raw_data.get(key, "")
    if res == "":
        return 0
    return float(res)
