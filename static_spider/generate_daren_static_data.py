#coding:utf-8
"""
@file:      gnerate_daren_static_data
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm Mac
@create:    2016/11/9 22:09
@description:
            --
"""

import os,pymysql,requests,json,time
from api.func import Timer,get_beijing_time
from ProdPageParser import ProdPageParser
from multiprocessing.dummy import Pool as ThreadPool

class DarenStaticDataGenerator:
    def __init__(self,start,end):
        self.start = start
        self.end = end
        self.white_users = self.load_white_users()

    def load_white_users(self):
        with open('./white_users','r') as f:
            return [ int(line.strip('\n')) for line in f.readlines() ]

    def mkdir_daren(self):
        time_str = get_beijing_time(format='%Y_%m_%d_%H_%M_%S')
        print(time_str)
        if 'DarenData' not in os.listdir('./'):
            os.mkdir('./DarenData')
        new_dir = './DarenData/{}'.format(time_str)
        os.mkdir(new_dir)
        self.root_dir = new_dir
        for sub_dir in ['CommDaRen','CommonDaV','CommonBaiMingDan']:
            if sub_dir not in os.listdir(new_dir):
                os.mkdir('{}/{}'.format(new_dir,sub_dir))

    def get_prod_info(self,prod_id):
        prod_url = 'http://uz.taobao.com/detail/{}'.format(prod_id)
        resp = requests.get(prod_url)
        if resp.status_code==404:
            #print('Fail crawl {}:{}'.format(prod_id,prod_url))
            return 404
        detail_page_html = resp.text
        prod = ProdPageParser(
            html=detail_page_html).to_dict()
        print('SUCCESS crawl {}: {}'.format(prod_id,prod_url))
        prod['darenNoteUrl'] = prod_url
        return prod

    def crawl_per_prod(self,prod_id):
        prod = self.get_prod_info(prod_id)
        if prod==404:
            return False
        if len(prod.keys())==2:
            #访问正常，但无效数据
            return True
        prod['darenNoteId'] = prod_id
        if not self.write_json(prod):
            return False
        for key in prod.keys():
            #print(key,prod[key])
            if isinstance(prod[key],str) and "'" in prod[key]:
                prod[key] = prod[key].replace("'",'')
        sql = "insert into t_daren_goodinfo(darenId,darenNoteId,darenNoteUrl,darenNoteTitle,darenNoteCover,darenNotePubDate,darenNoteReason,goodId,goodUrl,createTime) \
                VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')"\
                .format(
                    prod['userId'],prod['darenNoteId'],prod['darenNoteUrl'],\
                     prod['darenNoteTitle'],prod['darenNoteCover'],\
                     prod['darenNotePubDate'],prod['darenNoteReason'],\
                     prod['goodId'],prod['goodUrl'],get_beijing_time()
                )
        if prod['userId'] in self.white_users:
            sql_name = 'baimingdan.sql'
        else:
            sql_name = 'dav.sql'
        with open('{}/{}'.format(
                self.root_dir,sql_name),'ab') as f:
            f.write('{};'.format(sql).encode('utf-8'))
        if self.mysql:
            return self.save_to_mysql(sql)
        return False

    def save_to_mysql(self,sql):
        #print(sql)
        try:
            self.cur.execute(sql)
            print('save to mysql ok')
        except pymysql.err.IntegrityError:
            print('save to mysql : Duplicate')
        except Exception as e:
            print('error sql : {}\n{}'.format(sql,str(e)))

    def write_json(self,prod):
        userId = int(prod['userId'])
        prod['createTime'] = get_beijing_time()
        if userId in self.white_users:
            folder = 'CommonBaiMingDan'
        else:
            folder = 'CommonDaV'
        json_file_name = '{}/{}/{}.json'. \
            format(self.root_dir, folder, userId)
        write_path = '{}/{}'. \
            format(self.root_dir, folder)
        if json_file_name not in os.listdir(write_path):
            with open(json_file_name, 'w') as f:
                f.write('{"prods_list":[]}')
        try:
            jd = json.load(
                fp=open(json_file_name, 'r')
            )
        except json.decoder.JSONDecodeError:
            return False
        jd['prods_list'].append(prod)
        with open(json_file_name, 'w') as f:
            f.write(json.dumps(jd))
        return True

    def run(self,mysql=True,thread_cot=32):
        self.mysql = mysql
        self.mkdir_daren()
        if mysql==True:
            self.conn = pymysql.connect(
                host = '123.57.213.217',
                database = 'spiderpython',
                user = 'root',
                password = 'xingguang@123',
                charset = 'utf8',
                autocommit = True
            )
            self.cur = self.conn.cursor()
        pool = ThreadPool(thread_cot)
        cur = self.start
        dynamic_range_length = 100
        err_cot = 0
        success_cot = 0
        ex_tm = Timer()
        ex_tm.start()
        tm = Timer()
        while(cur<self.end):
            tm.start()
            little_range = range(cur,cur+dynamic_range_length)
            res = pool.map(self.crawl_per_prod,little_range)
            tm.end()
            ex_tm.end()
            success_cot += res.count(True)
            err_cot += res.count(False)
            cur += dynamic_range_length
            print('{}, {}, {}%, {} s, {} s'.format(
                success_cot,err_cot,
                int((success_cot/err_cot)*100),
                tm.gap, ex_tm.gap
            ))
            print('--------')
        pool.close()
        pool.join()

if __name__=="__main__":
    generator = DarenStaticDataGenerator(5732587480,57325881000)
    #generator.crawl_per_prod('5732587480')
    generator.run(mysql=False,thread_cot=32)
    #generator.load_white_users()