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
    darenId = models.CharField(max_length=500)#prod['userId']
    darenNoteId = models.CharField(max_length=500)
    darenNoteUrl = models.CharField(max_length=500)
    darenNoteTitle = models.CharField(max_length=500)
    darenNoteCover = models.CharField(max_length=500)
    darenNotePubDate = models.CharField(max_length=500)
    darenNoteReason = models.CharField(max_length=500)
    goodId = models.CharField(max_length=500)
    goodUrl = models.CharField(max_length=500)
    createTime = models.TimeField()

