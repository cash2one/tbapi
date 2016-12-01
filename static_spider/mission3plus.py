#coding:utf-8
"""
@file:      mission3plus
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-11-28 19:36
@description:
            --
"""
try:
    from .init_range_sql import get_conn
except:
    from init_range_sql import get_conn

import os,sys
sys.path.append(
    os.path.dirname(
        sys.path[0]
        ))
from api.func import Timer
from api.DarenPageParser import ProdsInfoGenerator
from multiprocessing.dummy import Pool as ThreadPool
import requests,random,pymysql

global index
index = 0
EX_THREAD_COT = 16

conn_pool = []

def init_conn(i):
    print('init conn: {} ok'.format(i))
    conn_pool.append({
        'conn':get_conn(),
        'status':0
        })

pool = ThreadPool(64)
pool.map(init_conn,range(100))
pool.close()
pool.join()


print('init db pool ok')

def get_random_conn():
    loop_cot=0
    while(1):
        loop_cot+=1
        busy_cot = 0
        free_cot = 0
        for conn in conn_pool:
            if conn['status']==1:
                busy_cot += 1
            else:
                free_cot += 1
        '''
        print(free_cot,busy_cot)
        '''
        for conn in conn_pool:
            if conn['status']==0:
                conn['status']=1
                return conn
        print('pool no free,wait..')
        time.sleep(2)

def get_unhandled_darenIds():
    connObj = get_random_conn()
    conn = connObj['conn']
    cur = conn.cursor()
    try:
        cur.execute(
            'select darenId from t_daren_note_task\
                order by updateTime'
        )
        ids = [ item[0] for item in cur.fetchall()]
    except Exception as e:
        print(str(e))
        ids = []
    cur.close()
    connObj['status']=0
    return ids



def insert_per_goods(kwargs):
    return insert_goods(**kwargs)

def insert_goods(darenId,darenNoteIds,table):
    connObj = get_random_conn()
    conn = connObj['conn']
    cur = conn.cursor()
    result = []
    for darenNoteId in darenNoteIds:
        sql = "insert into {}(`darenId`,`darenNoteId`) \
            VALUES ('{}','{}')".format(table,darenId,darenNoteId)
        #print(sql)
        try:
            cur.execute(sql)
            #conn.commit()
            print('insert {} ok'.format(darenNoteId))
            res = True
        except pymysql.err.IntegrityError as e:
            #print(str(e))
            res = False
        except Exception as e:
            print('insert error:{}'.format(str(e)))
            print(sql)
            res = False
        result.append(res)
    #print(result)
    #conn.commit()
    cur.close()
    connObj['status'] = 0
    return result


def get_good_ids(darenHomeUrl):
    for i in range(2):
        try:
            req = requests.get(darenHomeUrl,timeout=5)
            html = req.text
            break
        except:
            print('req error')
    try:
        ids = ProdsInfoGenerator(html_source=html).to_id_list()
        return ids
    except IndexError:
        return []
    except:
        return []

def mark_task_ok(darenId,db_use,crawl_cot,insert_cot,status,req_use):
    connObj = get_random_conn()
    conn = connObj['conn']
    cur = conn.cursor()
    sql = (
        "update t_daren_note_task set `timeuse`={},"
        "`crawl_cot`={},`insert_cot`={} "
        "where darenId='{}'"
    ).format(db_use+req_use,crawl_cot,insert_cot,darenId)
    status += '\t{}\t{}'.format(req_use,db_use)
    try:
        cur.execute(sql)
        conn.commit()
        print('{}\tupdate ok '.format(status))
    except Exception as e:
        print('update error:{}'.format(str(e)))
        print(sql)
    cur.close()
    connObj['status']=0

def crawl_per_daren(darenId):
    global index
    index += 1
    tm = Timer()
    tm.start()
    darenHomeUrl = 'http://uz.taobao.com/home/{}'.format(darenId)
    darenNoteIds = get_good_ids(darenHomeUrl)
    status = '{}\t{}\t{}\t{}'\
        .format(darenId,darenHomeUrl,index,len(darenNoteIds))
    pool = ThreadPool(8)
    goods = []
    for darenNoteId in darenNoteIds:
        goods.append({
            'darenId':darenId,
            'darenNoteId':darenNoteId,
            'table':'t_daren_goodinfo_02',
        })
    tm.end()
    req_use = tm.gap
    tm.start()
    res = insert_goods(darenId,darenNoteIds,'t_daren_goodinfo_02')
    #res = pool.map(insert_per_good,goods)
    tm.end()
    pool.close()
    pool.join()
    kvargs = {
        'darenId': darenId,
        'db_use': round(tm.gap,2),
        'crawl_cot': len(darenNoteIds),
        'insert_cot':res.count(True),
        'status': status,
        'req_use': req_use
    }
    mark_task_ok(**kvargs)


if __name__=="__main__":
    import time
    while(1):
        index = 0
        darenIds = get_unhandled_darenIds()
        ex_pool = ThreadPool(EX_THREAD_COT)
        ex_pool.map(crawl_per_daren,darenIds)
        print('one time loop end..')
        ex_pool.close()
        ex_pool.join()
        time.sleep(1)
