#coding:utf-8
"""
@file:      ProductPageSpider
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-11-02 22:30
@description:
        本模块包括处理jsonp的html字符串，以及对解析模块得到的数据进行封装
"""
from bs4 import BeautifulSoup as BS
from .ProductPageParser import ProductPageParser,Product
import requests
from multiprocessing.dummy import Pool as ThreadPool

class ProductPageSpider:
    def __init__(self,url):
        self.url = url
        self.domain = url.split('?')[0].split('/')[-2]
        print(self.domain)
        self.products_data = {}
        html = requests.get(self.url).text
        try:
            soup = BS(html,'lxml')
        except:
            soup = BS(html,'html.parser')
        self.jsonp_url = 'https://'+ self.domain + soup.select_one('#J_ShopAsynSearchURL')['value']
        print('jsonp url:',self.jsonp_url)

    def crawl_jsonp_page(self,page_index,just_for_page_num=False):
        #按每页爬取，首页返回总页数
        url = self.jsonp_url
        if page_index!=1:
            url += '&pageNo={}'.format(page_index)
        print('crawl page {}... {}'.format(page_index,url))
        page_prods= []
        jsonp_html = requests.get(url)\
                .text.replace('\\','').replace('|','')
        f = open('./sample2.html','w')
        f.write(jsonp_html)
        f.close()
        parser = ProductPageParser(
            from_web=True,
            html_source=jsonp_html
        )
        if not just_for_page_num:
            #只拿page_num时不要条目数据
            for sec in parser.sections:
                prod_info_dict = Product(sec).to_dict()
                if None==prod_info_dict['cmt_link']:
                    #这里判断已经到搜索至下方推荐条目，不再追加
                    break
                page_prods.append(prod_info_dict)
            self.products_data[page_index] = page_prods
            print('append page {} data ok!'.format(page_index))
        if page_index==1:
            return parser.page_num

    def get_page_num(self):
        return {'page_num':
            self.crawl_jsonp_page(
                page_index=1,just_for_page_num=True)
        }

    def run(self):
        self.page_num = self.crawl_jsonp_page(1)
        print('page num: {}'.format(self.page_num))
        if self.page_num < 16:
            thread_cot = self.page_num
        else:
            thread_cot = 16
        pool = ThreadPool(thread_cot)
        pool.map(self.crawl_jsonp_page,range(2,self.page_num+1))
        pool.close()
        pool.join()

    def get_products_info(self):
        #字典封装
        self.run()
        return {
            'page_nums': list(range(1,self.page_num+1)),
            'products': self.products_data
        }

if __name__=='__main__':
    #spider = ProductPageSpider(url='https://qyxcy.tmall.com/search.htm?search=y&orderType=newOn_desc&tsearch=y')
    spider = ProductPageSpider(url='https://yoho1314520.taobao.com/search.htm?spm=a1z10.1-c-s.0.0.hdbFzN&search=y&orderType=hotsell_desc')
    json = spider.get_page_num()
    #json = spider.get_products_info()
    print(json)