#coding:utf-8
"""
@file:      init_range_sql
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-11-22 21:45
@description:
            --
"""
import pymysql

conn = pymysql.connect(
    db = 'spiderpython',
    user = 'root',
    password = 'xingguang@123',
    host = '123.57.213.217',
    port = 3306
)

cur = conn.cursor()

def mark_flag(note_id):
    sql = (
        'insert into task_flag(note_id)'
        'VALUES ({})'
    ).format(note_id)
    print(sql)

start = 5400000000

end = 5500000000

from multiprocessing.dummy import Pool as ThreadPool


pool = ThreadPool(16)

pool.map(mark_flag,range(start,end))