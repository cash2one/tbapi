#coding:utf-8
"""
@file:      DarenPageSpider
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm Mac
@create:    2016/11/6 01:37
@description:
        达人主页商品爬虫
"""
from multiprocessing.dummy import Pool as ThreadPool
from .DarenPageParser import DarenPageParser,Product
from bs4 import BeautifulSoup
import requests,re

def request_with_ipad(url):
    return requests.get(url,
        headers={'user-agent': 'Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5")'}
    )


class DarenPageSpider:
    '''
        sample url:
            http://uz.taobao.com/home/86428989/
            http://ku.uz.taobao.com/
    '''
    def __init__(self,url):
        self.url = url
        self.json_data = []
        self.user_id = None
        self.rediret_domain = True
        # 表征是否会重定向个性域名，默认为真，
        # 只有在输入url为原地址且检测出user domain为空时，才置为假
        if 'home' in url:
            #识别为原地址
            self.user_id = self.url.split('/')[-2]
            user_domain = self.get_user_domain()
            if user_domain=="":
                # 未设置个性域名，url不作处理
                # 因为也可拿到数据，而存在个性域名时必须指向才有正确数据
                self.rediret_domain = False
                self.domain = url
            else:
                self.domain = 'http://{}.uz.taobao.com/'.format(user_domain)
            print(self.domain)
        else:
            #个性域名不做url处理
            self.domain = url

    def get_user_domain(self):
        #对url进行预处理，适应两种情况
        txt = request_with_ipad(self.url).text
        soup = BeautifulSoup(txt, 'html.parser')
        #print(soup)
        js_str = soup.find('script', text=re.compile('window.DAOGOU')).text
        words = re.split("domain: |,", js_str)
        #print(words)
        for word in words:
            #print(word)
            if "domain:" in word:
                print(word.strip())
                return word.split(":")[-1].strip("'")
        raise Exception('get user domain failed')

    def run(self):
        ct_url_ids = self.get_category_urls_id_names()
        if ct_url_ids==[]:
            #没有二级菜单时只能爬主页
            self.crawl_per_category(
                category_url_id_name = (
                    '{}index.htm?pageSize=500'.format(self.domain),
                    None,
                    '主页'
                )
            )
        else:
            if len(ct_url_ids)<16:
                extern_thread_cot = len(ct_url_ids)
            else:
                extern_thread_cot = 16
            pool = ThreadPool(extern_thread_cot)
            pool.map(self.crawl_per_category,ct_url_ids)
            pool.close()
            pool.join()

    def get_category_urls_id_names(self):
        #获取二级菜单
        return DarenPageParser(
                html_source=request_with_ipad(self.domain).text
            ).category_urls_id_names

    def crawl_per_category(self,category_url_id_name):
        # 爬取每个二级菜单下的商品信息
        # 先拿到总页数，在多线程分别爬取每页
        category_url = category_url_id_name[0]
        category_id = category_url_id_name[1]
        category_name = category_url_id_name[2]
        category_data = {
            'category_url': category_url,
            'category_id': category_id,
            'category_name': category_name,
            'page_nums': [],
            'page_data': {}
        }
        first_page_parser = DarenPageParser(
            html_source=request_with_ipad(category_url).text
        )
        page_num = first_page_parser.page_num
        if page_num==0:
            print('No items in this daren page')
            return
        print('page_index:{}  url:{}'\
                .format(page_num,category_url))
        category_data['page_nums'] = list(
            range(1,first_page_parser.page_num+1))
        cate_url_page_indexs = [
            (category_url,page_index,category_data)
                for page_index in
                    range(1,first_page_parser.page_num+1)
        ]
        #print(cate_url_page_indexs)
        if page_num<16:
            iner_cot = page_num
        else:
            iner_cot = 16
        pool = ThreadPool(iner_cot)
        pool.map(self.crawl_per_page,cate_url_page_indexs)
        pool.close()
        pool.join()
        self.json_data.append(category_data)

    def crawl_per_page(self,cate_url_page_index_data_dict):
        #爬取每页商品信息
        category_url = cate_url_page_index_data_dict[0]
        page_index = cate_url_page_index_data_dict[1]
        category_data = cate_url_page_index_data_dict[2]
        page_url = category_url + '&page={}'.format(page_index)
        page_parser = DarenPageParser(
            html_source=request_with_ipad(page_url).text
        )
        prods = page_parser.get_prods_list_by_json()
        # 能找到瀑布流（html中蕴含的json）直接通过其得到信息
        # 不能就做bs4解析拿信息（涉及到template 1 2 3的问题）
        if prods==[]:
            for sec in page_parser.sections:
                prod = Product(div_section=sec, domain=category_url)
                # prod.show_in_cmd()
                prods.append(prod.to_dict())
        print('crawl items: {} , url: {}'\
              .format(len(prods),page_url))
        category_data['page_data'][page_index] = prods

    def to_json(self):
        self.run()
        return {
            'daren_prods': self.json_data,
            'user_id': self.user_id
        }

if __name__=='__main__':
    url1 = 'http://yh123.uz.taobao.com/'
    url = 'http://uz.taobao.com/home/1060235927/'
    data = DarenPageSpider(url1).to_json()
    print(data)