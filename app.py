import time

from flask import Flask

import secret
from models.base_model import db
from utils import log

# 注册蓝图
# url_prefix 可以用来给蓝图中的每个路由加一个前缀
# import routes.index as index_view
from routes.index import main as index_routes
from routes.topic import main as topic_routes
from routes.reply import main as reply_routes
from routes.board import main as board_routes
from routes.message import main as mail_routes
from routes.setting import main as setting_routes
from routes.reset import main as reset_routes
from routes.resume import main as resume_routes
from routes.index import not_found


# @app.template_filter()
def count(input):
    log('count using jinja filter')
    return len(input)


def format_time(unix_timestamp):
    # 枚举
    # enum Year():
    #     2020
    #     0202
    # f = Year.2020
    f = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(unix_timestamp)
    formatted = time.strftime(f, value)
    return formatted


def configured_app():
    # web framework
    # web application
    # __main__
    app = Flask(__name__)
    # 设置 secret_key 来使用 flask 自带的 session
    app.secret_key = secret.secret_key
    # 数据返回顺序
    # mysql -> pymysql -> sqlalchemy -> route
    # 初始化顺序
    # app -> flask-sqlalchemy -> sqlalchemy -> pymysql -> mysql

    uri = 'mysql+pymysql://root:{}@localhost/bbs?charset=utf8mb4'.format(
        secret.database_password
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    db.init_app(app)

    register_routes(app)
    register_else(app)
    return app


def register_routes(app):

    # 注册蓝图
    # url_prefix 可以用来给蓝图中的每个路由加一个前缀

    app.register_blueprint(index_routes)
    app.register_blueprint(topic_routes, url_prefix='/topic')
    app.register_blueprint(reply_routes, url_prefix='/reply')
    app.register_blueprint(board_routes, url_prefix='/board')
    app.register_blueprint(mail_routes, url_prefix='/message')
    app.register_blueprint(setting_routes, url_prefix='/setting')
    app.register_blueprint(reset_routes, url_prefix='/reset')
    app.register_blueprint(resume_routes, url_prefix='/resume')
    log('url map', app.url_map)


def register_else(app):
    # 装饰器做 jinja filter
    # @app.template_filter()
    # def count(input):
    app.template_filter()(count)
    app.template_filter()(format_time)
    app.errorhandler(404)(not_found)

