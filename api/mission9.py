# -*- coding: utf-8 -*-
"""
@author:    panda0(pandaZW@icloud.com)

需求9: 淘宝商品资料抓取
~~~~~~~~~~~~~~~~

"""
try:
    from .SearchPageInfoGenerator import StoreInfoGenerator
except:
    from SearchPageInfoGenerator import StoreInfoGenerator
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
    print(url)
    print(r.status_code)
    r.id = id
    return r


class goodInfo:
    '''
    解析器
    获取商品信息

    '''

    def __init__(self, arg):
        r = get(arg)
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
        self.url = r.url
        self.is_tb = 'taobao' in r.url
        self.refund = None
        self.detailCommon = None
        self.list_dsr_info = None
        self.promotion = None
        self.generate_promotion()
        if self.is_tb:
            self.generate_refund()
            self.generate_detailCommon()
        else:
            self.generate_list_dsr()

    def generate_list_dsr(self):
        url = (
            'https://dsr-rate.tmall.com'
            '/list_dsr_info.htm?itemId={}&callback=jsonp'
        ).format(self.goodID)
        print(url)
        js = requests.get(url).text.split('jsonp(')[-1][:-2]
        print(js)
        jd = json.loads(js)
        self.comment_cot = jd['dsr']['rateTotal']

    @property
    def goodName(self):
        # 商品信息
        res = self.soup.find(id='J_Title').h3['data-title'].strip() if self.is_tb \
            else self.soup.select_one('.tb-detail-hd > h1').text.strip()
        return res

    @property
    def goodPrice(self):
        # 商品价格
        if self.promotion:
            return self.promotion['zkPrice']
        else:
            if self.is_tb:
                return float(self.soup.find(id='J_StrPrice').text.strip('¥'))
            else:
                return -1

    @property
    def shopName(self):
        # 店铺名
        res = self.soup.find(class_='tb-shop-name').text.strip() if self.is_tb\
            else self.soup.select_one('.slogo-shopname').text
        return res

    @property
    def shopLink(self):
        # 店铺链接
        res = self.soup.find(class_='tb-shop-name').a['href'] if self.is_tb\
            else self.soup.select_one('.slogo-shopname')['href']
        if res[0] == '/':
            res = 'https:' + res
        return res

    @property
    def sellerName(self):
        # 卖家名
        res = self.soup.find(class_='tb-shop-seller')\
            .a['title'].strip('掌柜:') if self.is_tb\
            else None
        return res

    @property
    def shopScores(self):
        # 卖家分
        if self.is_tb:
            shop_scores = self.soup.find(class_='tb-shop-rate').find_all('a')
            score = list(
                map(lambda i: float(i.get_text().strip().replace('\n', '')),
                    shop_scores))
            return score
        else:
            return [ round(float(item['title'][:-1]),3) for item
                        in self.soup.find_all('em',class_='count')]

    def generate_detailCommon(self):
        # 评论页面json数据
        if self.is_tb:
            request_url = 'https://rate.taobao.com/detailCommon.htm?auctionNumId=' + \
                str(self.goodID)
            print(request_url)
            raw = requests.get(request_url).text.split('(')[-1].split(')')[0]
            res = json.loads(raw)
            # 按照str格式化输出
            # print(json.dumps(res, sort_keys=True, indent=4, ensure_ascii=False))
        #print(res)
        else:
            res = None
        self.detailCommon = res

    @property
    def comment(self):
        # 评论json
        return self.detailCommon['data']['count'] if self.is_tb else None

    @property
    def impression(self):
        # 大家印象页面 list
        return self.detailCommon['data']['impress'] if self.is_tb else None

    @property
    def rate_of_good(self):
        # 计算好评率
        if self.is_tb:
            total = self.detailCommon['data']['count']['total']
            good = self.detailCommon['data']['count']['good']
            return round(good / total, 2)
        else:
            return -1

    def generate_refund(self):
        # 售后页面json
        if self.is_tb:
            url = 'https://rate.taobao.com/refund/refund_common.htm?auctionNumId=' + \
                str(self.goodID) + \
                '&userNumId=673837271&_ksTS=1479983685671_1994&callback=jsonp'
            #print('refund_url',url)
            raw = requests.get(url).text.split('jsonp(')[-1][:-1]
            res = json.loads(raw)
            # print(json.dumps(res, sort_keys=True, indent=4, ensure_ascii=False))
        else:
            res = None
        self.refund = res

    @property
    def refundSpeed(self):
        # 售后速度
        if self.is_tb:
            res = self.refund['refundSpeed'][
                'detailDateMap']['refundSpeed']['day']
        else:
            return -1
        return res

    @property
    def disputeRatio(self):
        # 纠纷率
        if self.is_tb:
            res = self.refund['disputeRatio']['base']['localVal']
        else:
            return -1
        return res

    @property
    def refundSale(self):
        # 售后率
        if self.is_tb:
            res = self.refund['refundSale']['base']['localVal']
        else:
            return -1
        return res

    def generate_promotion(self):
        # 促销信息
        self.promotion = StoreInfoGenerator(store_url=self.url).to_json()
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
        info = self.to_dict()
        for key in self.to_dict().keys():
            print('{}:\t{}'.format(key,info[key]))

    def to_dict(self):
        if self.is_tb:
            return {
                'good_name': self.goodName,
                'goodPrice': self.goodPrice,
                'shopName': self.shopName,
                'good_name': self.goodName,
                'shopLink': self.shopLink,
                'sellerName': self.sellerName,
                'shopScores': self.shopScores,
                'comment': self.comment,
                'impression': self.impression,
                'rate_of_good': self.rate_of_good,
                'refund': self.refund,
                'refundSpeed': self.refundSpeed,
                'disputeRatio': self.disputeRatio,
                'refundSale': self.refundSale,
                'promotion': self.promotion,
            }
        else:
            return {
                'good_name': self.goodName,
                'goodPrice': self.goodPrice,
                'shopName': self.shopName,
                'good_name': self.goodName,
                'shopLink': self.shopLink,
                #'sellerName': self.sellerName,
                'shopScores': self.shopScores,
                'comment_cot': self.comment_cot,
                'promotion': self.promotion,
                #'rate_total': self.rate_total
                #'impression': self.impression,
                #'rate_of_good': self.rate_of_good,
                #'refund': self.refund,
                #'refundSpeed': self.refundSpeed,
                #'disputeRatio': self.disputeRatio,
                #'refundSale': self.refundSale,
            }


if __name__ == "__main__":
    goodID = 539565305499  # tmall id
    #url = 'https://item.taobao.com/item.htm?id=539342473126'  # taobao link

    #goodInfo(get(url)).show()     # 按照url查询 tb


    goodInfo(get(goodID)).show()    # 按照ID查询 tmall

    '''
    天猫商品详情页面请求 价格 上下架时间 url：被ban
https://mdskip.taobao.com/core/initItemDetail.htm?cartEnable=true&isAreaSell=false&isForbidBuyItem=false&addressLevel=2&cachedTimestamp=1479971865613&isRegionLevel=false&service3C=true&household=false&tmallBuySupport=true&tryBeforeBuy=false&isSecKill=false&isPurchaseMallPage=false&sellerPreview=false&offlineShop=false&queryMemberRight=true&showShopProm=false&isApparel=false&isUseInventoryCenter=true&itemId=536138243373&callback=setMdskip&timestamp=1479985724377&isg=AhISz0J7KtXNvXOwqSG2Aypk4tL0ARa9&isg2=At3d6GRLWUpB5TLl4cPaOmeP7L-X3RFM0k_Q2p-iOzRjVv2IZ0ohHKvG5v0q
    '''
