from google.appengine.ext import ndb

class UserItem(ndb.Model):
    user_id = ndb.StringProperty()
    nick = ndb.StringProperty()

class UserRecord(ndb.Model):
    raw_data = ndb.JsonProperty()

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
def save_data(user, data):
    item = _get_user_item(user)
    if not item:
        return False
    return False
    UserRecord(data=data, parent=item.key).put()
    return True
