from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import *

from models.message import Messages
main = Blueprint('mail', __name__)


# 发送邮件
@main.route("/add", methods=["POST"])
def add():
    form = request.form.to_dict()
    u = current_user()

    receiver_name = form['receiver_name']
    receiver = User.one(username=receiver_name)
    receiver_id = int(receiver.id)

    # 发邮件
    Messages.send(
        title=form['title'],
        content=form['content'],
        sender_id=u.id,
        receiver_id=receiver_id
    )

    return redirect(url_for('.index'))


# 查看所有邮件
@main.route('/')
def index():
    u = current_user()

    send = Messages.all(sender_id=u.id)
    received = Messages.all(receiver_id=u.id)

    t = render_template(
        'mail/index.html',
        sended=send,
        received=received,
        bid=-1,
        user=u,
    )
    return t


# 查看一封邮件详细内容
@main.route('/view/<int:id>')
def view(id):
    message = Messages.one(id=id)
    u = current_user()

    if u.id in [message.receiver_id, message.sender_id]:
        return render_template('mail/detail.html',
                               message=message,
                               user=u,
                               bid=-1,
                               )
    else:
        return redirect(url_for('.index'))
