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
import requests


def request_with_ipad(url):
    return requests.get(url,
        headers={'user-agent': 'Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5")'}
    )


class DarenPageSpider:
    '''
        sample domain: http://ku.uz.taobao.com
    '''
    def __init__(self,domain):
        self.domain = domain
        self.json_data = []

    def get_category_urls_id_names(self):
        return DarenPageParser(
                html_source=request_with_ipad(self.domain).text
            ).category_urls_id_names

    def crawl_per_category(self,category_url_id_name):
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
        print('category_id: {} , category_url: {} '\
                .format(category_id,category_url))
        first_page_parser = DarenPageParser(
            html_source=request_with_ipad(category_url).text
        )
        page_num = first_page_parser.page_num
        print('page_num:{}'.format(page_num))
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
        category_url = cate_url_page_index_data_dict[0]
        page_index = cate_url_page_index_data_dict[1]
        category_data = cate_url_page_index_data_dict[2]
        page_url = category_url + '&page={}'.format(page_index)
        page_parser = DarenPageParser(
            html_source=request_with_ipad(page_url).text
        )
        sections = page_parser.sections
        print('crawl products_num: {}, url: {}'\
              .format(len(sections),page_url))
        prods = []
        for sec in sections:
            #Product(div_section=sec, domain=category_url).show_in_cmd()
            prods.append(
                Product(div_section=sec, domain=category_url).to_dict()
            )
        category_data['page_data'][page_index] = prods

    def run(self):
        ct_url_ids = self.get_category_urls_id_names()
        if len(ct_url_ids)<16:
            extern_thread_cot = len(ct_url_ids)
        else:
            extern_thread_cot = 16
        pool = ThreadPool(extern_thread_cot)
        pool.map(self.crawl_per_category,ct_url_ids)
        pool.close()
        pool.join()

    def to_json(self):
        self.run()
        print('全部爬取完成')
        return self.json_data

if __name__=='__main__':
    data = DarenPageSpider(domain='http://ku.uz.taobao.com').to_json()
    print(data)