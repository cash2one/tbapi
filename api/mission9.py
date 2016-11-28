# -*- coding: utf-8 -*-
"""
@author:    panda0(pandaZW@icloud.com)

需求9: 淘宝商品资料抓取
~~~~~~~~~~~~~~~~

"""

import requests
from bs4 import BeautifulSoup as bs
import json


def get(arg):
    '''
    判断是url或id， 获取soup 返回url, id
    '''
    if '.com' in str(arg):
        # url: get(url)
        # 提取出商品id
        url = arg
        # To Do
        id = url.split('id=')[1]
    else:
        # id: 拼接url
        url = 'https://item.taobao.com/item.htm?id='.join(['', str(arg)])
        id = arg
    r = requests.get(url)
    r.id = id
    return r


class goodInfo:
    '''
    解析器
    获取商品信息

    '''

    def __init__(self, r=None):
        if r.status_code is not 200:
            print('rq status Error')
            return
        else:
            try:
                self.soup = bs(r.text, 'lxml')
            except:
                self.soup = bs(r.text, 'html.parser')
        self.goodID = r.id

        # r.url 根据id 重定向 以此判断选择哪一个解析器
        # 如访问：https://item.taobao.com/item.htm?id=536138243373
        # r.url = 'https://detail.tmall.com/item.htm?id=536138243373'
        if 'tmall' in r.url:
            self.is_tb = False
        else:
            self.is_tb = True

    @property
    def goodName(self):
        # 商品信息
        res = self.soup.find(id='J_Title').h3['data-title'] if self.is_tb \
            else self.soup.select_one('.tb-detail-hd > h1 > a').text
        return res

    @property
    def goodPrice(self):
        # 商品价格
        res = self.soup.find(id='J_StrPrice').text if self.is_tb \
            else None
        # self.soup.select_one('#J_StrPriceModBox > dd').text
        return res

    @property
    def shopName(self):
        # 店铺名
        res = self.soup.find(class_='tb-shop-name').text.strip() if self.is_tb\
            else self.soup.select_one('.slogo-shopname').text
        return res

    @property
    def shopLink(self):
        # 店铺链接
        res = self.soup.find(class_='tb-shop-name').a['href']
        return res

    @property
    def sellerName(self):
        # 卖家名
        res = self.soup.find(class_='tb-shop-seller').a['title']
        return res

    @property
    def shopScores(self):
        # 卖家分
        shop_scores = self.soup.find(class_='tb-shop-rate').find_all('a')
        score = list(
            map(lambda i: float(i.get_text().strip().replace('\n', '')),
                shop_scores))
        return score

    @property
    def detailCommon(self):
        # 评论页面json数据
        if self.is_tb:
            request_url = 'https://rate.taobao.com/detailCommon.htm?auctionNumId=' + \
                str(self.goodID)
            raw = requests.get(request_url).text.split('(')[-1].split(')')[0]
            res = json.loads(raw)
            # 按照str格式化输出
            # print(json.dumps(res, sort_keys=True, indent=4, ensure_ascii=False))
        return res

    @property
    def comment(self):
        # 评论json
        return self.detailCommon['data']['count']

    @property
    def impression(self):
        # 大家印象页面 list
        return self.detailCommon['data']['impress']

    @property
    def rate_of_good(self):
        # 计算好评率
        total = self.detailCommon['data']['count']['total']
        good = self.detailCommon['data']['count']['good']
        return round(good / total * 100, 2)

    @property
    def refund(self):
        # 售后页面json
        if self.is_tb:
            url = 'https://rate.taobao.com/refund/refund_common.htm?auctionNumId=' + \
                str(self.goodID) + \
                '&userNumId=673837271&_ksTS=1479983685671_1994&callback=jsonp1995'
            raw = requests.get(url).text.split('jsonp1995(')[-1][:-1]
            res = json.loads(raw)
            # print(json.dumps(res, sort_keys=True, indent=4, ensure_ascii=False))
        return res

    @property
    def refundSpeed(self):
        # 售后速度
        if self.is_tb:
            res = self.refund['refundSpeed'][
                'detailDateMap']['refundSpeed']['day']
        return res

    @property
    def disputeRatio(self):
        # 纠纷率
        if self.is_tb:
            res = self.refund['disputeRatio']['base']['localVal']

        return res

    @property
    def refundSale(self):
        # 售后率
        if self.is_tb:
            res = self.refund['refundSale']['base']['localVal']
        return res

    # wrong
    # @property
    # def start_time(self):
    #     if self.is_tb:
    #         res = self.soup.find(id='J_sidebar_config').get('data-tbar')
    #         t = json.loads(res)['validTime']
    #     return t

    def show(self):
        # 测试打印
        print('\n********* New Good **************')
        print('Name:\t{}'.format(self.goodName))
        print('Price:\t{}'.format(self.goodPrice))
        print('ShopName:\t{}'.format(self.shopName))
        print('shopLink:\t{}'.format(self.shopLink))
        print('sellerName:\t{}'.format(self.sellerName))
        print('描述 服务 物流:\t{}'.format(self.shopScores))
        print('评论:\t{}\n'.format(self.comment))
        print('大家印象\t{}\n'.format(self.impression))
        print('好评率\t{}%'.format(self.rate_of_good))
        # print('售后服务情况 \t{}\n'.format(self.refund))
        print('售后速度\t{}天'.format(self.refundSpeed))
        print('纠纷率\t{}%'.format(self.disputeRatio))
        print('售后率\t{}%'.format(self.refundSale))
        # print('上架时间\t{}'.format(self.start_time))

if __name__ == "__main__":
    goodID = 536138243373  # tmall id
    url = 'https://item.taobao.com/item.htm?id=538180971307'  # taobao link

    goodInfo(get(url)).show()     # 按照url查询 tb

    #goodInfo(get(goodID)).show()    # 按照ID查询 tmall

    '''
    天猫商品详情页面请求 价格 上下架时间 url：被ban
https://mdskip.taobao.com/core/initItemDetail.htm?cartEnable=true&isAreaSell=false&isForbidBuyItem=false&addressLevel=2&cachedTimestamp=1479971865613&isRegionLevel=false&service3C=true&household=false&tmallBuySupport=true&tryBeforeBuy=false&isSecKill=false&isPurchaseMallPage=false&sellerPreview=false&offlineShop=false&queryMemberRight=true&showShopProm=false&isApparel=false&isUseInventoryCenter=true&itemId=536138243373&callback=setMdskip&timestamp=1479985724377&isg=AhISz0J7KtXNvXOwqSG2Aypk4tL0ARa9&isg2=At3d6GRLWUpB5TLl4cPaOmeP7L-X3RFM0k_Q2p-iOzRjVv2IZ0ohHKvG5v0q
    '''
