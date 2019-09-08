import os
import uuid
import time

from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    abort,
    send_from_directory,
    current_app)
from werkzeug.datastructures import FileStorage

from models.board import Board
from models.reply import Reply
from models.topic import Topic
from models.user import User
from routes import current_user, cache, new_csrf_token
# from routes import current_user

import json

from utils import log

main = Blueprint('index', __name__)

# import gevent

# 首页
@main.route("/")
def index():
    # time.sleep(0.5)
    u = current_user()
    if u is None:
        return redirect(url_for('.login_view'))
    else:
        return redirect(url_for('topic.index'))


@main.route("/login/view")
def login_view():
    return render_template("login.html")

# 登陆动作
@main.route("/login", methods=['POST'])
def login():
    form = request.form
    u = User.validate_login(form)
    if u is None:
        return redirect(url_for('.index'))
    else:
        # session 中写入 user_id 并用 cache 存储
        session_id = str(uuid.uuid4())
        key = 'session_id_{}'.format(session_id)
        log('index login key <{}> user_id <{}>'.format(key, u.id))
        cache.set(key, u.id)

        # 设置 cookie > response.set_cookie
        # 删除 cookie > response.delete_cookie
        redirect_to_index = redirect(url_for('topic.index'))
        response = current_app.make_response(redirect_to_index)
        response.set_cookie('session_id', value=session_id)
        # 转到 topic.index 页面
        return response


# 注册 view
@main.route("/register/view")
def register_view():
    return render_template('register.html')

# 注册动作
@main.route("/register", methods=['POST'])
def register():
    form = request.form.to_dict()
    # todo 判断用户名是否重复
    u = User.register(form)
    return redirect(url_for('.index'))


# 自己创立的 topic
def created_topic(user_id):
    # O(n)
    log('enter function created_topic')
    ts = Topic.all(user_id=user_id)
    log('function created_topic', ts, type(ts))
    return ts


# 自己回复过的 topic
def replied_topic(user_id):
    log('enter function replied_topic')
    ts = Topic.query\
        .join(Reply, Topic.id == Reply.topic_id)\
        .filter(Reply.user_id == user_id)\
        .all()
    log('function replied_topic', ts, type(ts))
    return ts


# 展示自己的资料
@main.route('/profile')
def profile():
    print('running profile route')
    u = current_user()
    if u is None:
        return redirect(url_for('.index'))
    else:
        created = created_topic(u.id)
        created.reverse()
        # log('profile created', created)
        replied = replied_topic(u.id)
        replied.reverse()
        # log('profile replied', replied)

        return render_template(
            'profile.html',
            user=u,
            created_topic=created,
            replied_topic=replied,
            bid=-1,
        )


# 展示其他用户详细资料
@main.route('/user/<int:id>')
def user_detail(id):
    u = User.one(id=id)
    if u is None:
        abort(404)
    else:
        created = created_topic(u.id)
        created.reverse()
        log('user_detail created_topic', created)

        replied = replied_topic(u.id)
        replied.reverse()
        return render_template('profile.html',
                               user=u,
                               created_topic=created,
                               replied_topic=replied,
                               bid=-1,
                               )


# 修改用户头像，保存到 images 文件夹下
@main.route('/image/add', methods=['POST'])
def avatar_add():
    file: FileStorage = request.files['avatar']
    suffix = file.filename.split('.')[-1]
    if suffix not in ['gif', 'jpg', 'jpeg']:
        abort(400)
        log('不接受的后缀, {}'.format(suffix))
    else:
        filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
        path = os.path.join('images', filename)
        file.save(path)

        u = current_user()
        User.update(u.id, image='/images/{}'.format(filename))

        return redirect(url_for('.profile'))


# 返回一张 images 文件夹下的图片
@main.route('/images/<filename>')
def image(filename):
    return send_from_directory('images', filename)


def not_found(e):
    return render_template('404.html')