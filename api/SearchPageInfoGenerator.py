#coding:utf-8
"""
@file:      SearchPageInfoGenerator
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.5
@editor:    PyCharm Mac
@create:    2016/11/2 02:13
@description:
        本模块用于调用淘宝后端的ajax接口，拼接二者的json做转发
"""

import requests,json

class StoreInfoGenerator:
    '''
        sample url: http://pub.alimama.com/promo/search/index.htm
        本页的加载流程分为两个ajax，一是基本信息，二是详情
        初始化此类后直接调用to_json()方法即可得到处理后的完整json
    '''
    def __init__(self,store_url):
        self.url = store_url
        self.user_view_url = None
        self.basic_info = None
        self.detail_info = None

    def generate_basic_info(self):
        #得到店铺基本信息
        json_url = 'http://pub.alimama.com/items/search.json?q={}'\
                            .format(self.url)
        self.user_view_url = 'http://pub.alimama.com/promo/search/index.htm?q={}'\
                            .format(self.url)
        #print(json_url)
        full_json = requests.get(json_url).text
        #print(full_json)
        jd = json.loads(full_json)
        #先将拿到的完整json转置为python字典，直接取第一个结果
        self.basic_info = jd['data']['pageList'][0]
        if len(jd['data']['pageList'])!=1:
            raise Exception('[Error] in get basic info: Multi Results')

    def generate_detail_info(self,seller_id):
        # 得到店铺细节信息
        if not seller_id:
            raise Exception('[Error] in get promote info: seller_id cannot be empty.')
        json_url = 'http://pub.alimama.com/pubauc/searchPromotionInfo.json?oriMemberId={}'\
                        .format(seller_id)
        self.temp_url = json_url
        full_json = requests.get(json_url).text
        #print(full_json)
        jd = json.loads(full_json)['data']
        #由于淘宝该接口是允许多商铺并行请求的，会返回列表，但我们只需要第一个
        #故对该字典做如下处理
        for key in jd.keys():
            jd[key] = jd[key][0]
        self.detail_info = jd

    def run(self):
        try:
            self.generate_basic_info()
        except:
            #此情况是店铺url链接错误，淘宝后端无法匹配得唯一条目（可能给予关键词重定向产生多项条目）
            print('Error in generate_basic_info():\n\tMaybe no located result and redirect worked in this page:{}'\
                    .format(self.user_view_url))
            return -1
        try:
            self.generate_detail_info(
            seller_id=self.basic_info['sellerId'])
        except Exception as e:
            print('Error in generate_detail_info():  page in :{}\n\t{}'\
                  .format(self.temp_url,str(e)))
            return -2
        #print('basic',self.basic_info)
        #print('detail',self.detail_info)
        for key in self.detail_info.keys():
            self.basic_info[key] = self.detail_info[key]
        return 1

    def to_json(self):
        res = self.run()
        if res==1:
            print('Result OK')
            return self.basic_info
        else:
            return res


if __name__=="__main__":
    url = 'https://detail.tmall.com/item.htm?id=44895723989'
    json = StoreInfoGenerator(url).to_json()
    print(json)