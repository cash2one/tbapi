#coding:utf-8
"""
@file:      models.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-11-14 16:07
@description:
        db models by django
"""

from django.db import models
from django.utils import timezone

class t_daren_goodinfo(models.Model):
    class Meta:
        db_table = 't_daren_goodinfo'
    darenId = models.CharField()#prod['userId']
    darenNoteId = models.CharField()
    darenNoteUrl = models.CharField()
    darenNoteTitle = models.CharField()
    darenNoteCover = models.CharField()
    darenNotePubDate = models.CharField()
    darenNoteReason = models.CharField()
    goodId = models.CharField()
    goodUrl = models.CharField()
    createTime = models.TimeField(default=timezone.now())

