from google.appengine.ext import ndb

class UserItem(ndb.Model):
    user_id = ndb.StringProperty()
    nick = ndb.StringProperty()

class UserRawData(ndb.Model):
    raw_data = ndb.JsonProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

class UserTrainingDay(ndb.Model):
    date = ndb.DateProperty()
    points = ndb.FloatProperty()

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
