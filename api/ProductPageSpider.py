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

class ProductPageSpider:
    def __init__(self,url):
        self.url = url
        self.domain = url.split('?')[0].split('/')[-2]
        self.products_data = {}
        soup = BS(requests.get(self.url).text,'html.parser')
        self.jsonp_url = 'https://'+ self.domain + soup.select_one('#J_ShopAsynSearchURL')['value']
        print('jsonp url:',self.jsonp_url)

    def crawl_jsonp_page(self,page_index,just_for_page_num=False):
        #按每页爬取，首页返回总页数
        url = self.jsonp_url
        if page_index!=1:
            url += '&pageNo={}'.format(page_index)
        page_prods= []
        parser = ProductPageParser(
            from_web=True,
            html_source=requests.get(url)\
                .text.replace('\\','').replace('|','')
        )
        if not just_for_page_num:
            #只拿page_num时不要条目数据
            for sec in parser.sections:
                prod_info_dict = Product(sec).to_dict()
                for key in prod_info_dict.keys():
                    #不允许信息不全的条目加入
                    #这里判断已经到搜索至下方推荐条目，不再追加
                    if None == prod_info_dict[key]:
                        break
                page_prods.append(prod_info_dict)
            self.products_data[page_index] = page_prods
        if page_index==1:
            return parser.page_num

    def get_page_num(self):
        return {'page_num':
            self.crawl_jsonp_page(
                page_index=1,just_for_page_num=True)
        }

    def run(self):
        self.page_num = self.crawl_jsonp_page(1)
        for page_index in range(2,self.page_num+1):
            self.crawl_jsonp_page(page_index)

    def get_products_info(self):
        #字典封装
        self.run()
        return {
            'page_num': self.page_num,
            'products': self.products_data
        }

if __name__=='__main__':
    spider = ProductPageSpider(url='https://qyxcy.tmall.com/search.htm?search=y&orderType=newOn_desc&tsearch=y')
    json = spider.get_page_num()
    #json = spider.get_products_info()
    print(json)