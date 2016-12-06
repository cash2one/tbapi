#coding:utf-8
"""
@file:      mission8
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-12-06 17:05
@description:
            --
"""
import requests,re,json
from bs4 import BeautifulSoup

class ItemPageParser:
    '''
        sample url: https://item.taobao.com/item.htm?id=44404410356
    '''
    def __init__(self,item_page_url=None,item_id=None):
        url = item_page_url
        if item_id:
             url = 'https://item.taobao.com/item.htm?id={}'.format(item_id)
        r = requests.get(url)
        url = r.url
        print('url:\t{}'.format(url))
        self.soup = BeautifulSoup(r.text,'html.parser')
        jsonp_url_txt = self.soup.find(
            text=re.compile('async_dc')).split("Hub.config.set('async_dc', {")[1]
        jsonp_url = 'http:'+re.split("api   : '|}\);|\n",jsonp_url_txt)[3][:-1]
        print('jsonp_url:\t{}\n'.format(jsonp_url))
        jsonp_src = re.split('\r\nvar SHOP_DC = ',requests.get(jsonp_url).text)[1].strip()[:-1]
        jsonp_src = jsonp_src.replace('\\r\\n','').replace('\t','')
        #print(jsonp_src,'\njson_src below')
        self.jd = json.loads(jsonp_src,strict=False)
        self.headArchive = BeautifulSoup(
            self.jd['headArchive'],'html.parser')

    def print_html(self):
        for key in self.jd.keys():
            with open('./jd/{}.html'.format(key),'w') as f:
                try:
                    f.write(self.jd[key])
                except:
                    pass

    def get_user_rate_id(self):
        return self.headArchive.find('a',attrs={'href':re.compile('rate.taobao.com/user-rate-')})['href']\
                .split('rate-')[1].split('.')[0]

    def get_shop_id(self):
        shop_url = self.soup.find('form',attrs={'target':'_top'})['action']
        #print(shop_url)
        return re.split('//shop|.t',shop_url)[1]

class UserRateInfoGenerator:
    '''
        sample url: https://rate.taobao.com/user-rate-UvCNWMCxbMmIYvNTT.htm?spm=2013.1.0.0.XBd2dO
    '''
    def __init__(self,rate_page_url=None,user_rate_id=None,
            shop_id=None,from_web=True,cookie=None):
        if not rate_page_url:
            rate_page_url = 'https://rate.taobao.com' \
                    '/user-rate-{}.htm'.format(user_rate_id)
        try:
            self.ShopService4_api_URL = (
                'https://rate.taobao.com'
                '/ShopService4C.htm?userNumId={}'
                '&shopID={}&qq-pf-to=pcqq.c2c'
            ).format(user_rate_id,shop_id)
        except Exception as e:
            print(str(e))
            self.ShopService4_api_URL = None
        print('ShopService4_api_URL:\t{}'.format(self.ShopService4_api_URL))
        if from_web:
            src = requests.get(
                url=rate_page_url,
                headers={
                    'cookie':cookie
                }
            ).text
        else:
            print('read local')
            with open('./sample_user_rate.html','r') as f:
                src = f.read()
        self.soup = BeautifulSoup(src,'html.parser')
        self.jd = {}
        self.generate_jd()

    def generate_jd(self):
        try:
            txt = self.soup.find(text=re.compile('"userID": '))
            print(txt)
            self.jd = json.loads(txt)
            print('jd:{}'.format(self.jd.keys()))
        except Exception as e:
            print('rate page generate_jd error:{}'\
                  .format(str(e)))

    def get_ShopService4_api_json(self):
        if self.ShopService4_api_URL==None:
            url = (
                'https://rate.taobao.com/'
                'ShopService4C.htm?userNumId={}'
                '&shopID={}'
            ).format(self.jd['userID'],self.jd['shopID'])
        else:
            url = self.ShopService4_api_URL
        print(url)
        return json.loads(requests.get(url).text)




parser = ItemPageParser(item_id=44404410356)

parser.print_html()

user_id = parser.get_user_rate_id()

print(user_id)

shop_id = parser.get_shop_id()

print(shop_id)

info_engine = UserRateInfoGenerator(
    user_rate_id = parser.get_user_rate_id(),
    shop_id = parser.get_shop_id(),
    from_web = True
)

jd = info_engine.get_ShopService4_api_json()

print(jd)
