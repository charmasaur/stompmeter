from google.appengine.ext import ndb
import datetime

class UserItem(ndb.Model):
    user_id = ndb.StringProperty()
    nick = ndb.StringProperty()

class UserRawData(ndb.Model):
    raw_data = ndb.JsonProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

class UserTrainingDay(ndb.Model):
    date = ndb.DateProperty()
    points = ndb.FloatProperty()

class UserTrainingWeek(ndb.Model):
    week_end_date = ndb.DateProperty()
    week_points = ndb.FloatProperty()

def _get_user_parent_key():
    return ndb.Key('UserParent', 'default')

def _get_user_id(user):
    return user.user_id()

def _get_user_item(user):
    results = UserItem.query(
            filters=UserItem.user_id == _get_user_id(user),
            ancestor=_get_user_parent_key()).fetch()
    if len(results) > 1:
        raise Exception("Duplicate user detected!")

    if len(results) == 1:
        return results[0]

    return None

def set_nick(user, nick):
    item = _get_user_item(user)
    if not item:
        # Add a new item
        item = UserItem(user_id=user.user_id(), nick=None, parent=_get_user_parent_key())

    item.nick = nick
    item.put()

def get_nick(user):
    item = _get_user_item(user)
    if not item:
        return None
    return item.nick

# Returns True iff successful
def save_raw_data(user, raw_data):
    item = _get_user_item(user)
    if not item:
        return False
    UserRawData(raw_data=raw_data, parent=item.key).put()
    return True

# Returns (True, daily points) if successful, (False, 0) otherwise
def save_points(user, date, points):
    item = _get_user_item(user)
    if not item:
        return False
    existing = UserTrainingDay.query(
            filters=UserTrainingDay.date == date,
            ancestor=item.key).fetch()
    if len(existing) > 1:
        raise Exception("Duplicate training record for the same user and day!")
    elif len(existing) == 1:
        day = existing[0]
    else:
        day = UserTrainingDay(date=date, parent=item.key)
        day.points = 0
    day.points += points
    day.put()
    return True, day.points

# Returns None if the user doesn't exist, or a list of at most max_results
# (date, points) tuples otherwise.
def get_recent_points(user, max_results):
    item = _get_user_item(user)
    if not item:
        return None
    days = UserTrainingDay.query(ancestor=item.key).order(-UserTrainingDay.date).fetch(max_results)
    return [(day.date, day.points) for day in days]

# Returns a dictionary of nick to (dictionary of date to points in the week
# ending with that date). The dictionary will only be correctly populated for
# weeks for which snapshot_week_scores has been called.
def get_scoreboard():
    training_weeks = (UserTrainingWeek
            .query(ancestor=_get_user_parent_key())
            .fetch())
    result_dict = {}
    for training_week in training_weeks:
        nick = training_week.parent.get().nick
        if nick in result_dict:
            weeks_dict = result_dict[nick]
        else:
            weeks_dict = {}
            result_dict.update({nick : weeks_dict})
        weeks_dict.update(
                {training_week.week_end_date : training_week.week_points})
    return result_dict

# Takes a snapshot of all scores from the given week (up to and including the
# specified date).
def snapshot_week_scores(week_end_date):
    # Map from user item key to the corresponding training week.
    item_key_to_training_week = {}
    # First see if we've already taken a snapshot of this week. In that case we
    # want to reset then update those items rather than create new ones.
    training_weeks = (UserTrainingWeek
            .query(ancestor=_get_user_parent_key())
            .filter(UserTrainingWeek.week_end_date == week_end_date)
            .fetch())
    for training_week in training_weeks:
        item_key_to_training_week.update({training_week.parent : training_week})
        training_week.week_points = 0

    # Fetch all training days in the specified week.
    week_start_date = week_end_date - datetime.timedelta(6)
    training_days = (UserTrainingDay
            .query(ancestor=_get_user_parent_key())
            .filter(UserTrainingDay.date >= week_start_date)
            .filter(UserTrainingDay.date < week_end_date)
            .fetch())
    for training_day in training_days:
        item_key = training_day.key.parent()
        if item_key in item_key_to_training_week:
            training_week = item_key_to_training_week[item_key]
        else:
            training_week = UserTrainingWeek(
                    week_end_date=week_end_date,
                    week_points=0,
                    parent=item_key)
            item_key_to_training_week.update({item_key : training_week})
        training_week.week_points += training_day.points

    # Save the weeks.
    for training_week in item_key_to_training_week.values():
        training_week.put()
