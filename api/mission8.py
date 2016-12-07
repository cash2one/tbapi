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
    def __init__(self,item_url=None,item_id=None,
            shop_url=None,shop_id=None):
        if shop_url or shop_id:
            if shop_id:
                shop_url = 'https://shop{}.taobao.com/'.format(shop_id)
            soup = BeautifulSoup(
                requests.get(shop_url).text,'html.parser')
            #print(soup)
            try:
                item_url = soup.find(
                    'a',attrs={'href':re.compile('item.htm\?id=')}
                )['href']
                if 'http' not in item_url:
                    item_url = 'https:' + item_url
                print('item_page_url:{}'.format(item_url))
            except Exception as e:
                print(str(e))
        url = item_url
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
        print('asyn_json_version:{}'.format(self.jd['categoryName']))
        self.headArchive = BeautifulSoup(
            self.jd['headArchive'],'html.parser')

    def get_rate_info(self):
        #print(self.headArchive)
        rate_info = []
        if '基础' in self.jd['categoryName']:
            dynamic_css_name = 'shop-rate'
        else:
            dynamic_css_name = 'shop-dynamic-score'
        for item in self.headArchive.select_one(
                '.{}'.format(dynamic_css_name)).find_all('li'):
            item_txt = item.text.strip()
            print(item_txt)
            if '基础' in self.jd['categoryName']:
                info = {
                    'title': item_txt[:4],
                    'score': item_txt[4:7],
                    'compare': item_txt[11:13],
                    'rate': re.split('于|%',item_txt)[-2] + '%',
                    'src': item_txt
                }
            else:
                info = {
                    'title': item_txt[:4],
                    'score': item_txt[4:7],
                    'compare': item_txt[10:12],
                    'rate': re.split('于|%',item_txt)[-2] + '%',
                    'src': item_txt
                }
            print(info)
            rate_info.append(info)
        return rate_info

    def print_html(self):
        for key in self.jd.keys():
            with open('api/jd/{}.html'.format(key),'w') as f:
                try:
                    f.write(self.jd[key])
                except:
                    pass

    def get_user_rate_id(self):
        return self.headArchive.find('a',
            attrs={'href':re.compile('rate.taobao.com/user-rate-')})['href']\
                .split('rate-')[1].split('.')[0]

    def get_shop_id(self):
        params = self.soup.find('meta',
                attrs={'name':'microscope-data'})['content'].split(';')
        for param in params:
            if 'shop' in param:
                return param.split('=')[1]



class UserRateInfoGenerator:
    '''
        sample url: https://rate.taobao.com/user-rate-UvCNWMCxbMmIYvNTT.htm?spm=2013.1.0.0.XBd2dO
    '''
    def __init__(self,rate_page_url=None,user_rate_id=None,
            shop_id=None,from_web=True,cookie=None):
        self.cookie = cookie
        if not rate_page_url:
            rate_page_url = 'https://rate.taobao.com' \
                    '/user-rate-{}.htm'.format(user_rate_id)
        try:
            self.ShopService4_api_URL = (
                'https://rate.taobao.com'
                '/ShopService4C.htm?userNumId={}'
                '&shopID={}&qq-pf-to=pcqq.c2c'
            ).format(user_rate_id,shop_id)
            self.refundIndex_api_URL = (
                'https://tosp.taobao.com/json/'
                'refundIndex.htm?shopId={}'
                '&businessType=1&callback=jsonp'
            ).format(shop_id)
        except Exception as e:
            print(str(e))
            self.ShopService4_api_URL = None
            self.refundIndex_api_URL = None
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
        return {
            'data': json.loads(requests.get(url).text),
            'api_url': url
        }

    def get_refundIndex_api_json(self):
        if self.refundIndex_api_URL == None:
            url = (
                'https://tosp.taobao.com/json/'
                'refundIndex.htm?shopId={}'
                '&businessType=1&callback=jsonp'
                '&_ksTS=1481097662269_130'
            ).format(self.jd['shopID'])
        else:
            url = self.refundIndex_api_URL
        print('refundIndex_api_URL: {}'.format(url))
        json_src = requests.get(url,
            headers = {
                'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                'cookie': self.cookie
            }
        ).text
        try:
            json_src = json_src.strip('typeof jsonp != "undefined" && jsonp(').strip()[:-2]
            print('json_src: {}\n'.format(json_src))
            return {
                'data':json.loads(json_src)['data'],
                'api_url': url
            }
        except:
            return {
                'success':False,
                'api_url': url,
                'message':'you could add cookie in request to get it.'
            }


if __name__=="__main__":

    #parser = ItemPageParser(shop_url='https://fishercoffee.taobao.com/')

    parser = ItemPageParser(shop_id=33121581)

    #parser = ItemPageParser(shop_url='https://fishercoffee.taobao.com/')

    parser.print_html()

    rate_info = parser.get_rate_info()

    print('rate_info: {}'.format(rate_info))

    user_id = parser.get_user_rate_id()

    print(print('user_id: {}'.format(user_id)))

    shop_id = parser.get_shop_id()

    print(print('shop_id: {}'.format(shop_id)))

    info_engine = UserRateInfoGenerator(
        user_rate_id = parser.get_user_rate_id(),
        shop_id = parser.get_shop_id(),
        from_web = True,
        cookie='cna=WBtLENHT0gACAdoD81QRJlpm; thw=cn; miid=106180397974956847; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; _m_user_unitinfo_=center; OUTFOX_SEARCH_USER_ID_NCOO=1980377882.2647953; _m_h5_tk=16472c390931315c3a95f3be2713badf_1480746764886; _m_h5_tk_enc=4f73c5e0b42f86dd967dc4b84eb4ac19; cq=ccp%3D1; v=0; uc3=sg2=BdS%2F5ECky2XG6j4oZ2dYnthzgZLeo6goHj5WH6aLuTg%3D&nk2=oYMpAx0d%2FJc%3D&id2=UoYY5MmCAv4tgg%3D%3D&vt3=F8dARHGxqqUMteh1BrQ%3D&lg2=UtASsssmOIJ0bQ%3D%3D; hng=CN%7Czh-cn%7CCNY; existShop=MTQ4MTA5ODA4Mw%3D%3D; uss=U7lSBcOx6BQEIqoO0qMiHMF6tCvFRr5bdWrn2M7GUE0J0ALt2KOvACwqMQ%3D%3D; lgc=%5Cu9646%5Cu9633%5Cu554A%5Cu554A; tracknick=%5Cu9646%5Cu9633%5Cu554A%5Cu554A; cookie2=15e762ee7298b399eed1942d93dabe8f; sg=%E5%95%8A76; mt=np=&ci=18_1&cyk=0_0; cookie1=W8rgeeHfM3k55SslW9iKOxLw531yPjJlVO4FdaDuJrA%3D; unb=1767700837; skt=64c9eb2525cafe43; t=310bef43ab6503c90f10aee8974a5287; _cc_=WqG3DMC9EA%3D%3D; tg=0; _l_g_=Ug%3D%3D; _nk_=%5Cu9646%5Cu9633%5Cu554A%5Cu554A; cookie17=UoYY5MmCAv4tgg%3D%3D; uc1=cookie14=UoW%2FXG%2B%2F9jfuzw%3D%3D&lng=zh_CN&cookie16=W5iHLLyFPlMGbLDwA%2BdvAGZqLg%3D%3D&existShop=true&cookie21=UIHiLt3xThH8t7YQoFNq&tag=3&cookie15=WqG3DMC9VAQiUQ%3D%3D&pas=0; _tb_token_=e4eb8717677ee; l=ApGRzdJN1FZpqpHpBCglTyRmIZcr/gVw; isg=AgUFcKLf8cOwitWZB5xS1abCFEFAQblUCyt6VgdqwTxLniUQzxLJJJN83nWS'
    )

    jd = info_engine.get_ShopService4_api_json()

    print('ShopService4_api_json:',jd)

    jd = info_engine.get_refundIndex_api_json()

    print('refundIndex_api_json:',jd)
