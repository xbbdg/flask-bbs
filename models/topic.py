import time

from sqlalchemy import String, Integer, Column, Text, UnicodeText, Unicode

from models.base_model import SQLMixin, db
from models.user import User
from models.reply import Reply
from utils import log


class Topic(SQLMixin, db.Model):
    views = Column(Integer, nullable=False, default=0)
    title = Column(Unicode(50), nullable=False)
    content = Column(UnicodeText, nullable=False)
    user_id = Column(Integer, nullable=False)
    board_id = Column(Integer, nullable=False)

    @classmethod
    def new(cls, form, user_id):
        form['user_id'] = user_id
        m = super().new(form)
        return m

    @classmethod
    def get(cls, id):
        m = cls.one(id=id)
        m.views += 1
        m.save()
        return m

    def user(self):
        u = User.one(id=self.user_id)
        return u

    def replies(self):
        ms = Reply.all(topic_id=self.id)
        return ms

    def reply_count(self):
        count = len(self.replies())
        return count

    def last_active_time(self):
        t = int(time.time())
        hours = (t - self.created_time) // 3600
        log('last_active_time', hours)
        return hours

    def last_reply_user(self):
        rs = self.replies()
        rid_list = [r.id for r in rs]
        if len(rid_list) > 0:
            index = rid_list.index(max(rid_list))
            r = rs[index]
            u = r.user()
            return u
