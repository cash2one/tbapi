#coding:utf-8
"""
@file:      KickTaskManager
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm Mac
@create:    2016/11/22 23:37
@description:
            --
"""

import os,sys
sys.path.append(
    os.path.dirname(
        sys.path[0]
    )
)

from generate_daren_static_data import DarenStaticDataGenerator

import random,time,gc
import pymysql
def get_conn():
    conn = pymysql.connect(
        db = 'spiderpython',
        user = 'root',
        password = 'xingguang@123',
        host = '123.57.213.217',
        port = 3306
    )
    conn.autocommit=True
    return conn

def get_max_grade():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        'select max(grade) from task_flag WHERE is_crawled=0'
    )
    data = cur.fetchall()[0][0]
    return data

def get_unfinished_range():
    conn = get_conn()
    cur = conn.cursor()
    sql = 'select `left`,`right`,`id` \
        from task_flag where is_crawled=0 \
        and grade = {}'.format(get_max_grade())
    print(sql)
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def get_spefic_range(leftest,rightest):
    conn = get_conn()
    cur = conn.cursor()
    sql = 'select `left`,`right`,`id` \
        from task_flag where is_crawled=0 \
        and id>{} and id<{} limit 100'.format(
        get_max_grade(),
        leftest,rightest
    )
    print(sql)
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def mark_ok(id,success_cot):
    conn = get_conn()
    cur = conn.cursor()
    sql = 'update task_flag set `is_crawled`=1 , `success_cot`={} \
                WHERE `id`={}'.format(success_cot,id)
    print(sql)
    cur.execute(sql)
    print('update {} ok'.format(id))
    conn.commit()
    cur.close()
    conn.close()

def run(big_loop=True,leftest=None,rightest=None):
    while(1):
        try:
            if big_loop:
                range = random.choice(get_unfinished_range())
            else:
                range = random.choice(get_spefic_range(leftest,rightest))
            print(range)
            left = range[0]
            right = range[1]
            id = range[2]
            #mark_ok(id,2)
            try:
                success_cot = DarenStaticDataGenerator(
                        left,right).run(
                    mysql=True,
                    thread_cot=64,
                    use_proc_pool=False,
                    use_email=True,
                    dynamic_range_length=right-left,
                    err_print=True,
                    visit_shuffle=False,
                    save_db_type=0,
                    debug=True,
                    save_by_django=False
                )
                mark_ok(id,success_cot)
            except Exception as e:
                print(str(e))
            finally:
                gc.collect()
        except:
            pass


