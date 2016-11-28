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
import pymysql,time

def get_conn():
    while(1):
        try:
            conn = pymysql.connect(
                db = 'spiderpython',
                user = 'root',
                password = 'xingguang@123',
                host = '123.57.213.217',
                port = 3306
            )
            conn.autocommit=True
            return conn
        except:
            print('db conn error')
            pass
        time.sleep(1)


def mark_flag(left):
    conn = get_conn()
    cur = conn.cursor()
    right = left + 100000
    grade = int(left/100000000)
    sql = (
        'insert into task_flag(`left`,`right`,`grade`,`index`)'
        ' VALUES ({},{},{},{})'
    ).format(left,right,grade,grade)
    print(sql)
    try:
        cur.execute(sql)
        conn.commit()
        print('save ok')
    except Exception as e:
        print(str(e))
    cur.close()
    conn.close()

if __name__=="__main__":

    start = 900000000

    end =   6000000000

    gap = 100000


    '''
    lefts = list(range(start,end,gap))

    for j in lefts:
        print(j,j+gap)
    '''

    from multiprocessing.dummy import Pool as ThreadPool


    pool = ThreadPool(32)

    pool.map(mark_flag,range(start,end,gap))
