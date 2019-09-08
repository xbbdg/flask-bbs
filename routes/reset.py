import os
import uuid

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

from models.reply import Reply
from models.topic import Topic
from models.user import User
from models.message import Messages
from routes import current_user, cache
from routes import current_user

import json

from utils import log

main = Blueprint('reset', __name__)

# 输入用户名找回密码界面
@main.route("/forget")
def forget():
    return render_template('forget.html')

# 发送重置验证 email 到邮箱
@main.route("/mail", methods=['POST'])
def send_mail():
    form = request.form.to_dict()
    username = form.get('username')
    u = User.one(username=username)
    email = form.get('email')

    if email == u.email:
        token = str(uuid.uuid4())

        cache.set(token, u.id)
        Messages.send(
            title='reset password',
            content='https://yivocs.cn/reset/view?token={}'.format(token),
            sender_id=u.id,
            receiver_id=u.id
        )
        return redirect(url_for('index.index'))
    else:
        return redirect('404')


# 重置密码页面 view
@main.route("/view")
def reset_view():
    token = request.args.get('token')
    log('reset view', token)

    if cache.exists(token):
        return render_template('reset.html', token=token)
    else:
        return redirect('404')


# reset 更新用户信息
@main.route("/reset", methods=['POST'])
def reset():
    token = request.form.get('token')
    password = request.form.get('password')
    if cache.exists(token):
        u = User.one(id=cache.get(token))
        u.reset_password(password)
        cache.delete(token)
        return redirect(url_for('index.index'))
    else:
        redirect('404')