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

#from generate_daren_static_data import DarenStaticDataGenerator

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
        'select max(grade) from task_flag'
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


def run():
    while(1):
        range = random.choice(get_unfinished_range())
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
       

def per_proc_run(proc_id):
    try:
        run()
        gc.collect()
    except Exception as e:
        print(str(e))

if __name__=="__main__":

    from multiprocessing import Pool as ProcPool

    use_proc = False

    if use_proc:
        proc_pool = ProcPool(2)

    import time
    while(1):
        if use_proc:
            proc_pool.map(per_proc_run,range(4))
            proc_pool.close()
            proc_pool.join()
        per_proc_run(1)
        time.sleep(1)
