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
)

from werkzeug.datastructures import FileStorage


from models.user import User
from models.topic import Topic
from models.reply import Reply
from routes import current_user


from utils import log

main = Blueprint('setting', __name__)


# setting 页面 view
@main.route("/")
def index():
    u = current_user()
    return render_template("setting.html", user=u, bid=-1)


# 修改用户名，用户签名动作
@main.route("/change", methods=['POST'])
def change():
    u = current_user()

    form = request.form
    log('change', form)
    u.username = form.get('name')
    u.signature = form.get('signature')
    u.save()
    return redirect(url_for('.index'))


# 用户修改密码动作
@main.route("/change_password", methods=['POST'])
def change_password():
    u = current_user()
    form = request.form
    log('change form', form)
    old_pass = form.get('old_pass')
    new_pass = form.get('new_pass')
    log('change_password', old_pass, new_pass, u.password)
    if u.change_password(form):
        return redirect(url_for('index.index'))
    else:
        return redirect('404.html')


# 用户修改头像动作
@main.route("/change_avatar", methods=['POST'])
def change_avatar():
    file: FileStorage = request.files['avatar']
    suffix = file.filename.split('.')[-1]
    if suffix not in ['gif', 'jpg', 'jpeg']:
        abort(400)
        log('不接受的后缀, {}'.format(suffix))
    else:
        filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
        path = os.path.join('static/img', filename)
        file.save(path)

        u = current_user()
        User.update(u.id, image='/static/img/{}'.format(filename))

        return redirect(url_for('.index'))