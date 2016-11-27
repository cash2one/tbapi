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
import pymysql,requests

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
        and `left`>{} and `right`<{} limit 100'.format(
        leftest,rightest
    )
    print(sql)
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def mark_ok(id,success_cot,ip,timeuse,db_ip,db_use_time,req_use_time):
    conn = get_conn()
    cur = conn.cursor()
    sql = "update task_flag set `is_crawled`=1 , `success_cot`={}, \
                `timeuse`={},`ip`='{}',`insert_db_ip`='{}',\
                `db_use_time`='{}',`request_use_time`='{}'\
                WHERE `id`={}"\
                    .format(success_cot,timeuse,ip,db_ip,db_use_time,req_use_time,id)
    print(sql)
    cur.execute(sql)
    print('update {} ok'.format(id))
    conn.commit()
    cur.close()
    conn.close()

def mark_running(id):
    conn = get_conn()
    cur = conn.cursor()
    sql = 'update task_flag set `is_crawled`=2 WHERE `id`={}'.format(id)
    print(sql)
    cur.execute(sql)
    print('mark {} runnning ok'.format(id))
    conn.commit()
    cur.close()
    conn.close()


def load_white_users():
    for maybe_path in ['./white_users', 'static_spider/white_users']:
        try:
            with open(maybe_path, 'r') as f:
                return [int(line.strip('\n')) for line in f.readlines()]
        except:
            continue
    return []

def get_ip():
    try:
        return requests.get('https://api.ipify.org/',timeout=15).text
    except:
        return None


from ORM import url


def run(big_loop=True,leftest=None,rightest=None,thread_cot=64):
    ip = get_ip()
    print(ip)
    while(1):
        try:
            if big_loop:
                ranges = get_unfinished_range()
            else:
                ranges = get_spefic_range(leftest,rightest)
            range = random.choice(ranges)
            print(range)
            #mark_running(id=range[2])
            #mark_ok(id,2)
            try:
                params = DarenStaticDataGenerator(
                    start=range[0],
                    end=range[1],
                    #end=range[0]+1000,
                    white_users=load_white_users()
                ).run(
                    mysql=True,
                    thread_cot=thread_cot,
                    use_proc_pool=False,
                    use_email=True,
                    dynamic_range_length=100000,
                    err_print=False,
                    visit_shuffle=False,
                    save_db_type=0,
                    debug=False,
                    save_by_django=False
                )
                mark_ok(ip=ip,id=range[2],success_cot=params['success_cot'],
                        timeuse=int(params['timeuse']),db_ip=url,
                        db_use_time=params['db_use_time'],req_use_time=params['req_use_time']
                        )
            except Exception as e:
                print(str(e))
            del ranges
            del params
        except:
            time.sleep(2)


