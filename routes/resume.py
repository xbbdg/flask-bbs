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

main = Blueprint('resume', __name__)


@main.route("/")
def index():
    log('job')
    return render_template("resume.html")