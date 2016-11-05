#coding:utf-8
"""
@file:      DarenPageParser
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm Mac
@create:    2016/11/6 01:42
@description:
        用于解析达人页的商品列表
"""
from bs4 import BeautifulSoup
from .decorators import except_return_none
ERN_METHOD = lambda func:except_return_none(func,ModelName='Product')

class DarenPageParser:
    def __init__(self,html_source=None,from_web=True):
        if not from_web:
            with open('./daren.html','rb') as f:
                html_source = f.read()
        try:
            self.soup = BeautifulSoup(html_source,'lxml')
        except:
            self.soup = BeautifulSoup(html_source,'html.parser')

    @property
    @ERN_METHOD
    def sections(self):
        try:
            return self.soup.select('.J_SiteSItem')
        except:
            return self.soup.select('.water-item')

    @property
    @ERN_METHOD
    def page_num(self):
        try:
            return int(self.soup.select_one('.count').text.strip('共').strip('页'))
        except:
            return int(self.soup.select_one('.paginator').find_all('a')[-2].text)

    @property
    def category_urls_id_names(self):
        #在解析首页时，返回该商铺的子标签信息元组(url,id)
        #注意为了使请求数最少，每页的请求size调至最大的500
        try:
            return [
                ( 'http:'+a['href']+'&page_size=500', a['href'].split('=')[-1], a.text )
                    for a in self.soup.select_one('.dz_dhh').find_all('a')
            ][1:-1]
        except:
            print('No sub category in this daren home page')
            return []


class Product:
    def __init__(self,div_section,domain):
        #由片段div,以及域名来初始化该类
        self.sec = div_section
        self.domain = domain

    @property
    @ERN_METHOD
    def descr(self):
        # 描述
        return self.sec.select_one('.item-desc').text.strip()

    @property
    @ERN_METHOD
    def id(self):
        # 编号
        return int(self.sec.select_one('.img-wrap')['href'].split('/')[-2])

    @property
    @ERN_METHOD
    def pic_url(self):
        # 图片地址
        return 'http://'+self.sec.find('img')['src'][2:]

    @property
    @ERN_METHOD
    def detail_link(self):
        # 详情页链接
        return self.domain+self.sec.select_one('.img-wrap')['href']

    @property
    @ERN_METHOD
    def focus_cot(self):
        # 关注数目
        return int(self.sec.select_one('.J_FocusItem').text)

    def show_in_cmd(self):
        # 测试打印
        print('\n*********New Product**************')
        print('descr:\t{}'.format(self.descr))
        print('id:\t{}'.format(self.id))
        print('pic_url:\t{}'.format(self.pic_url))
        print('detail_link:\t{}'.format(self.detail_link))
        print('focus_cot:\t{}'.format(self.focus_cot))

    def to_dict(self):
        return {
            'descr': self.descr,
            'id': self.id,
            'pic_url': self.pic_url,
            'detail_link': self.detail_link,
            'focus_cot': self.focus_cot
        }

if __name__=="__main__":
    import requests
    domain = 'http://ku.uz.taobao.com'
    html = requests.get(domain).text
    parser = DarenPageParser(html_source=html)
    #print(parser.sections)
    #print(parser.page_num)
    print(parser.category_urls_ids)
    '''
    for sec in parser.sections:
        Product(div_section=sec,domain=domain).show_in_cmd()
    '''