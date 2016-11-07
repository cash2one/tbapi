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
import json
from bs4 import BeautifulSoup
from .decorators import except_return_none
ERN_METHOD = lambda func:except_return_none(func,ModelName='DarenPageParser')

class DarenPageParser:
    def __init__(self,html_source=None,from_web=True,redirect_domain=False):
        if not from_web:
            with open('./daren.html','rb') as f:
                html_source = f.read()
        self.html_source = html_source
        try:
            self.soup = BeautifulSoup(html_source,'lxml')
        except:
            self.soup = BeautifulSoup(html_source,'html.parser')

    @property
    def template_type(self):
        if self.soup.select('.water-item')!=[]:
            #sample url: http://youup.uz.taobao.com/
            return 1
        if self.soup.select('.J_SiteSItem')!=[]:
            # sample url: http://chaoliudapei.uz.taobao.com/
            return 2
        if self.soup.select('.li-ite')!=[]:
            return 3
        #-1时初步可推断主页无条目
        return -1

    @property
    @ERN_METHOD
    def sections(self):
        #包含所有商品列表的 div
        return self.soup.select('.J_SiteSItem')

    @property
    @ERN_METHOD
    def page_num(self):
        #本页所表征的页数
        try:
            if self.template_type==2:
                return int(self.soup.select_one('.count').text.strip('共').strip('页'))
            if self.template_type==1:
                return int(self.soup.select_one('.paginator').find_all('a')[-2].text)
            if self.template_type==-1:
                return 0
        except:
            return 1

    @property
    def category_urls_id_names(self):
        #在解析首页时，返回该商铺的子标签信息元组(url,id)
        #注意为了使请求数最少，每页的请求size调至最大的500
        print('template type: {}'.format(self.template_type))
        #仅支持category
        try:
            return [
                ( 'http:'+a['href']+'&page_size=500', a['href'].split('=')[-1], a.text )
                    for a in self.soup.select_one('.dz_dhh').find_all('a')
            ][1:-1]
        except:
            pass
        #未支持tag
        '''
        if self.type==2:
            tag_alist = self.soup.select_one('.site-cate-item').find_all('a')
            print(tag_alist)
            return [
                ('http:' + a['href'] + '&page_size=500', a['href'].split('=')[-1], a.text)
                    for a in tag_alist
            ][1:-1]
        '''
        print('No sub category in this daren home page')
        return []

    def get_prods_list_by_json(self):
        #第二阶段对json数据的直接索取（不通过product解析类）
        if self.template_type==-1:
            return []
        else:
            return ProdsInfoGenerator(
                html_source=self.html_source
            ).to_list()


class ProdsInfoGenerator:
    def __init__(self,html_source):
        #print(html_source)
        self.json_str = html_source.split('daogouContents :   ')[1]\
                            .split('-->\r\n<')[0]
        self.pre_handle()

    @ERN_METHOD
    def pre_handle(self):
        self.jds = []
        for prod in self.json_str.split('}, {'):
            # print(prod)
            jd = {}
            for kv in prod.split(', '):
                # print(kv)
                k = kv.split('=')[0].strip()
                try:
                    v = kv.split('=')[1].strip()
                except:
                    continue
                if '\r' in v:
                    continue
                if v == 'null':
                    v = None
                try:
                    v = int(v)
                except:
                    pass
                jd[k] = v
            #print(jd)
            self.jds.append(jd)

    def to_list(self):
        return self.jds



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
        # 转为字典
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
    print(parser.category_urls_id_names)
    '''
    for sec in parser.sections:
        Product(div_section=sec,domain=domain).show_in_cmd()
    '''