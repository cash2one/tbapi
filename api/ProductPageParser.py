#coding:utf-8
"""
@file:      ProductsParser.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-11-02 21:58
@description:
        本模块包括店铺商品页的解析器，以及逻辑商品类
"""
from bs4 import BeautifulSoup
from .decorators import except_return_none
ERN_METHOD = lambda func:except_return_none(func,ModelName='Product')

class ProductPageParser:
    '''
        本类并非解析原页面 https://qyxcy.tmall.com/search.htm?spm=a1z10.3-b-s.w4011-15377984973.225.8r6Wz3&search=y&orderType=newOn_desc&pageNo=2&tsearch=y#anchor
        解析模版渲染前得到的jsonp中的html字符串
    '''
    def __init__(self,html_source=None,from_web=True):
        if not from_web:
            with open('./sample.html','rb') as f:
                html_source = f.read()
        try:
            self.soup = BeautifulSoup(html_source,'lxml')
        except:
            self.soup = BeautifulSoup(html_source,'html.parser')

    @property
    @ERN_METHOD
    def sections(self):
        #商品html div集合
        return self.soup.select('.item')

    @property
    def page_num(self):
        #页数
        return int(self.soup.select('.pagination > a')[-2].text)


class Product:
    def __init__(self,sec):
        self.sec = sec

    @property
    @ERN_METHOD
    def id(self):
        return int(self.sec['data-id'])

    @property
    @ERN_METHOD
    def sales(self):
        #总销量
        return int(self.sec.select_one('.sale-num').text)

    @property
    @ERN_METHOD
    def title(self):
        #品名
        return self.sec.select_one('.item-name').text.strip()

    @property
    @ERN_METHOD
    def price(self):
        #价格
        return float(self.sec.select_one('.c-price').text.strip())

    @property
    @ERN_METHOD
    def link(self):
        #商品链接
        return 'http:'+self.sec.select_one('.item-name')['href']

    @property
    def cmt_cot(self):
        try:
            return int(self.sec.select_one('.title').find('a').text.split(' ')[-1])
        except:
            pass

    @property
    def cmt_link(self):
        try:
            return 'http:'+self.sec.select_one('.title').find('a')['href']
        except:
            pass

    @property
    def img_src(self):
        return 'http:'+self.sec.find('img')['data-ks-lazyload']

    def to_dict(self):
        return {
            'sales':self.sales,
            'title':self.title,
            'price':self.price,
            'link':self.link,
            'cmt_cot':self.cmt_cot,
            'cmt_link':self.cmt_link,
            'img_src':self.img_src
        }

    def show_in_cmd(self):
        #测试打印
        print('\n*********New Product**************')
        print('id:\t{}'.format(self.id))
        print('link:\t{}'.format(self.link))
        print('sales:\t{}'.format(self.sales))
        print('title:\t{}'.format(self.title))
        print('price:\t{}'.format(self.price))
        print('img_src:\t{}'.format(self.img_src))
        print('cmt_cot:\t{}'.format(self.cmt_cot))
        print('cmt_link:\t{}'.format(self.cmt_link))


if __name__=="__main__":
    parser = ProductPageParser(from_web=False)
    num = parser.page_num
    print(num)
    for sec in parser.sections:
        Product(sec).show_in_cmd()
        #info_dict = Product(sec).to_dict()
