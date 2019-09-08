from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from models.base_model import db
from models.reply import Reply
from routes import *

from models.topic import Topic
from models.board import Board

main = Blueprint('topic', __name__)

# 论坛首页，区别了板块，展示 topic
@main.route("/")
def index():
    board_id = int(request.args.get('board_id', -1))
    if board_id == -1:
        ms = Topic.all()
    else:
        ms = Topic.all(board_id=board_id)
    # ms.reverse() 的返回值是 none
    ms.reverse()
    token = new_csrf_token()
    bs = Board.all()
    u = current_user()
    return render_template("topic/index.html", user=u, ms=ms, token=token, bs=bs, bid=board_id)


# topic 详细信息
@main.route('/<int:id>')
def detail(id):
    m = Topic.get(id)
    u = current_user()
    bid = m.board_id
    b = Board.one(id=bid)
    # 传递 topic 的所有 reply 到 页面中
    return render_template("topic/detail.html", topic=m, user=u, bid=bid, b=b)


# 删除 topic 动作
@main.route("/delete")
@csrf_required
def delete():
    id = int(request.args.get('id'))
    u = current_user()
    log('删除 topic 用户是', u, id)
    try:
        Topic.query.filter_by(id=id).delete()
        # raise Exception('垃圾异常')
        Reply.query.filter_by(topic_id=id).delete()
        db.session.commit()
    except Exception:
        db.session.rollback()
    return redirect(url_for('.index'))


# 新建帖子 view
@main.route("/new")
def new():
    board_id = int(request.args.get('board_id'))
    bs = Board.all()

    token = new_csrf_token()
    u = current_user()
    return render_template("topic/new.html", user=u, bs=bs, token=token, bid=board_id)


# 新建帖子动作
@main.route("/add", methods=["POST"])
@csrf_required
def add():
    form = request.form.to_dict()
    log('topic.add, form', form)
    u = current_user()
    log('topic.add, user', u)
    t = Topic.new(form, user_id=u.id)
    log('topic.add, topic', t)
    return redirect(url_for('.index'))
