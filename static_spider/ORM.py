#coding:utf-8
"""
@file:      ORM
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm Mac
@create:    2016/11/22 23:55
@description:
            db models by sqlalchemy
"""

from sqlalchemy import (
    Column, Integer, String
)
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class DarenGoodInfo(Base):
    __tablename__ = 't_daren_goodinfo'

    id = Column(Integer,primary_key=True,autoincrement=True)
    darenId = Column(String)
    darenNoteId = Column(String)
    darenNoteUrl = Column(String)
    darenNoteTitle = Column(String)
    darenNoteCover = Column(String)
    darenNotePubDate = Column(String)
    darenNoteReason = Column(String)
    goodId = Column(String)
    goodUrl = Column(String)
    createTime = Column(String)
    goodNoteDetailStep = Column(Integer)




mysql_url = (
    'mysql://{}:{}@{}:{}/{}'
).format(
    'root','xingguang@123',
    '123.57.213.217',3306,'spiderpython',
)

print(mysql_url)

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
Session = sessionmaker()
Session.configure(
    bind = create_engine(
        name_or_url=mysql_url,echo=True
    )
)
