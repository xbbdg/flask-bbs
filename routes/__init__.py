import uuid
from functools import wraps

import redis
from flask import session, request, abort

from models.user import User
from utils import log


def current_user():
    if 'session_id' in request.cookies:
        session_id = request.cookies['session_id']
        # s = Session.one_for_session_id(session_id=session_id)
        key = 'session_id_{}'.format(session_id)
        user_id = int(cache.get(key))
        log('current_user key <{}> user_id <{}>'.format(key, user_id))
        u = User.one(id=user_id)
        return u
    else:
        return None

def csrf_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.args['token']
        u = current_user()
        log('csrf_required token={}, cache.exists={}'.format(token, cache.exists(token)))
        log('csrf_required cache.get={}, u.id={}'.format(cache.get(token), u.id))
        # cache.exists() 存在则返回 1
        if cache.exists(token) and int(cache.get(token)) == u.id:
            cache.delete(token)
            return f(*args, **kwargs)
        else:
            abort(401)

    return wrapper


def new_csrf_token():
    u = current_user()
    token = str(uuid.uuid4())
    cache.set(token, u.id)
    return token


cache = redis.StrictRedis()