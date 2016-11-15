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

import sys,os
up_level_N = 2
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
    sys.path.append(root_dir)

import pymysql,requests,json,time
from api.func import Timer,get_beijing_time,request_with_ipad
from api.models import t_daren_goodinfo
from .Email import Email
from .ProdPageParser import ProdPageParser
from multiprocessing.dummy import Pool as ThreadPool

class DarenStaticDataGenerator:
    def __init__(self,start,end):
        self.start = start
        self.end = end
        self.gap = end - start
        self.white_users = self.load_white_users()
        print('load white users: {}'.format(
            len(self.white_users)))

    def load_white_users(self):
        for maybe_path in ['./white_users','static_spider/white_users']:
            try:
                with open(maybe_path,'r') as f:
                    return [ int(line.strip('\n')) for line in f.readlines() ]
            except:
                continue
        return []

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
        resp = request_with_ipad(prod_url)
        if resp.status_code==404:
            #print('Fail crawl {}:{}'.format(prod_id,prod_url))
            return 404
        detail_page_html = resp.text
        prod = ProdPageParser(
            html=detail_page_html).to_dict()
        print('[{}/{}] SUCCESS crawl {}: {}'\
              .format(prod_id-self.start,self.gap,prod_id,prod_url))
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
        if int(prod['userId']) in self.white_users:
            sql_name = 'baimingdan.sql'
        else:
            sql_name = 'dav.sql'
        with open('{}/{}'.format(
                self.root_dir,sql_name),'ab') as f:
            f.write('{};'.format(sql).encode('utf-8'))
        if self.mysql:
            #self.save_to_mysql(sql)
            self.save_to_mysql_by_django_orm(prod)
        if int(prod['userId']) in self.white_users:
            return 'bmd add'
        else:
            return 'dav add'

    def save_to_mysql_by_sql(self,sql):
        #print(sql)
        try:
            self.cur.execute(sql)
            print('save to mysql ok')
        except pymysql.err.IntegrityError:
            print('save to mysql : Duplicate')
        except Exception as e:
            print('error in save to mysql:{}'.format(str(e)))

    def save_to_mysql_by_django_orm(self,prod):
        db_info = t_daren_goodinfo()
        #db_info.createTime = prod['createTime']
        db_info.darenId = prod['userId']
        db_info.darenNoteId = prod['darenNoteId']
        db_info.darenNoteUrl = prod['darenNoteUrl']
        db_info.darenNoteTitle = prod['darenNoteTitle']
        db_info.darenNoteCover = prod['darenNoteCover']
        db_info.darenNotePubDate = prod['darenNotePubDate']
        db_info.goodId = prod['goodId']
        db_info.goodUrl = prod['goodUrl']
        try:
            db_info.save()
            print('save to mysql : Ok')
        except Exception as e:
            #print(str(e))
            print('save to mysql : Duplicate')

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

    def send_mail(self,subject,content,mail_address):
        emailAI = Email(
            receiver = mail_address,
            sender = 'luyangaini@vip.qq.com',
            subject = subject,
            content = content
              )
        emailAI.conn_server(
            host='smtp.qq.com',
            port = 587
        )
        emailAI.login(
            username='luyangaini@vip.qq.com',
            password='ptuevbbulatcbcfh'
        )
        emailAI.send()
        emailAI.close()

    def run(self,mysql=True,thread_cot=32,dynamic_range_length=1000):
        self.mysql = mysql
        self.dynamic_range_length = dynamic_range_length
        self.mkdir_daren()
        if mysql:
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
        err_cot = 0
        success_cot = 0
        ex_tm = Timer()
        ex_tm.start()
        tm = Timer()
        while(cur<self.end):
            tm.start()
            little_range = list(range(
                cur,cur+dynamic_range_length))
            res = pool.map(self.crawl_per_prod,little_range)
            tm.end()
            ex_tm.end()
            dav_success = res.count('dav add')
            bmd_success = res.count('bmd add')
            gap_fail = res.count(False)
            success_cot += (dav_success+bmd_success)
            err_cot += gap_fail
            print('{}, {}, {}%, {} s, {} s'.format(
                success_cot,err_cot,
                int((success_cot/err_cot)*100),
                tm.gap, ex_tm.gap
            ))
            content = '达人历史从 {} 到 {} , 总计{}个\n有白名单 {} 条，大v {} 条，共用时 {} 秒'.format(
                cur,cur+dynamic_range_length,dynamic_range_length,bmd_success,dav_success,tm.gap
            )
            #print(content)
            cur += dynamic_range_length
            self.send_mail(
                subject='达人历史抓取数据[{}]'.format(get_beijing_time()),
                content = content,
                mail_address = '763038567@qq.com'
            )
            print('--------')
        self.send_mail(
                subject='本次达人历史抓取数据完成[{}]'.format(get_beijing_time()),
                content = 'rt',
                mail_address = '763038567@qq.com'
            )
        pool.close()
        pool.join()

if __name__=="__main__":
    generator = DarenStaticDataGenerator(5732587480,57325881000)
    #generator.crawl_per_prod('5732587480')
    generator.run(mysql=False,thread_cot=32,dynamic_range_length=1000)
    #generator.load_white_users()
