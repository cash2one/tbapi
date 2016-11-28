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

from api.func import Timer
from api.DarenPageParser import ProdsInfoGenerator
from multiprocessing.dummy import Pool as ThreadPool
import requests


EX_THREAD_COT = 32


def get_unhandled_darenIds():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        'select darenId from t_daren_note_task where\
            is_crawled=0 or is_crawled is NULL limit 16'
    )
    ids = [ item[0] for item in cur.fetchall()]
    cur.close()
    conn.close()
    return ids

def insert_per_good(kvargs):
    return insert_one_good(**kvargs)

def insert_one_good(darenId,darenNoteId,table):
    conn = get_conn()
    cur = conn.cursor()
    sql = "insert into {}(`darenId`,`darenNoteId`) \
        VALUES ('{}','{}')".format(table,darenId,darenNoteId)
    #print(sql)
    try:
        cur.execute(sql)
        conn.commit()
        print('insert {} ok'.format(darenNoteId))
        res = True
    except Exception as e:
        print(str(e))
        print(sql)
        res = False
    cur.close()
    conn.close()
    return res

def get_good_ids(darenHomeUrl):
    for i in range(10):
        try:
            req = requests.get(darenHomeUrl,timeout=10)
            html = req.text
            break
        except:
            print('req error')
    try:
        ids = ProdsInfoGenerator(html_source=html).to_id_list()
        print(ids)
        return ids
    except IndexError:
        return []

def mark_task_ok(darenId,timeuse,crawl_cot,insert_cot):
    conn = get_conn()
    cur = conn.cursor()
    sql = (
        "update t_daren_note_task set `timeuse`={},"
        "`is_crawled`=1,`crawl_cot`={},`insert_cot`={} "
        "where darenId='{}'"
    ).format(timeuse,crawl_cot,insert_cot,darenId)
    try:
        cur.execute(sql)
        conn.commit()
        print('update {} ok '.format(darenId))
    except Exception as e:
        print(str(e))
        print(sql)
    cur.close()
    conn.close()

def crawl_per_daren(darenId):
    tm = Timer()
    tm.start()
    darenHomeUrl = 'http://uz.taobao.com/home/{}'.format(darenId)
    print(darenHomeUrl)
    darenNoteIds = get_good_ids(darenHomeUrl)
    print(len(darenNoteIds))
    pool = ThreadPool(32)
    goods = []
    for darenNoteId in darenNoteIds:
        print(darenNoteId)
        goods.append({
            'darenId':darenId,
            'darenNoteId':darenNoteId,
            'table':'t_daren_goodinfo_02',
        })
    res = pool.map(insert_per_good,goods)
    tm.end()
    pool.close()
    pool.join()
    kvargs = {
        'darenId': darenId,
        'timeuse': round(tm.gap/EX_THREAD_COT,2),
        'crawl_cot': len(darenNoteIds),
        'insert_cot':res.count(True)
    }
    mark_task_ok(**kvargs)


if __name__=="__main__":
    while(1):
        darenIds = get_unhandled_darenIds()
        if len(darenIds)<16:
            EX_THREAD_COT = len(darenIds)
        else:
            EX_THREAD_COT = 16
        ex_pool = ThreadPool(EX_THREAD_COT)
        ex_pool.map(crawl_per_daren,darenIds)
        ex_pool.close()
        ex_pool.join()