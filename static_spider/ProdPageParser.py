#coding:utf-8
"""
@file:      ProdPageParser
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm Mac
@create:    2016/11/10 02:53
@description:
        处理商品主页需要静态html解析的页面
"""

from bs4 import BeautifulSoup as BS
from api.decorators import except_return_none
from api.func import get_beijing_time

ERN_METHOD = lambda func:except_return_none(func,ModelName='ProdPageParser')

class ProdPageParser:
    '''
        sample url :http://uz.taobao.com/detail/5715026746/
        请注意：
            形如http://qzktt.uz.taobao.com/detail/5715054207/
            的商品主页有个性域名，前端html有json可以捕获，处理方法在DarenPageParser中有模块处理
        输出类似：
            darenNoteId：5622015512
            {
                "darenNoteCover":"//gw1.alicdn.com/tfscom/tuitui/TB2GD6krVXXXXXXXpXXXXXXXXXX_!!0-dgshop.jpg",
                "darenNotePubDate":1466870400000,
                "darenNoteReason":"纯白的色调，给人很纯洁的感觉。及脚踝的长度，恰到好处的修饰身材，露出纤细的双腿，更加显瘦。简洁干练的衬衫领，更加优雅。",
                "goodId":"534444090570",
                "goodNoteDetailStep":3,
                "goodUrl":"//item.taobao.com/item.htm?id=534444090570",
                "id":2127842
            }
    '''
    def __init__(self,html=None,from_web=True):
        if not from_web:
            with open('prod_sample.html','rb') as f:
                html = f.read()
        try:
            self.soup = BS(html,'lxml')
        except:
            self.soup = BS(html,'html.parser')

    @property
    @ERN_METHOD
    def userId(self):
        return int(self.soup.select_one('.avatar-wrap')['href'].split('/')[-2])

    @property
    @ERN_METHOD
    def darenNoteCover(self):
        return self.soup.select_one('.img-wrap > img')['data-src']

    @property
    @ERN_METHOD
    def darenNotePubDate(self):
        return self.soup.select_one('.pub-time').text.strip()[5:]

    @property
    @ERN_METHOD
    def darenNoteReason(self):
        return self.soup.select_one('.desc').text.strip()

    @property
    @ERN_METHOD
    def goodId(self):
        return int(self.soup.select_one('.info > a')['data-id'].split('_')[-1])

    @property
    def goodUrl(self):
        try:
            return self.soup.select_one('.info > a')['href']
        except:
            pass

    @property
    def darenNoteTitle(self):
        try:
            return self.soup.select_one('.yaHei-title > a').text.strip()
        except:
            pass

    def to_dict(self):
        if self.goodUrl==None:
            return {
                'result': None
            }
        return {
            "darenNoteCover": self.darenNoteCover,
            "darenNotePubDate": self.darenNotePubDate,
            "darenNoteReason": self.darenNoteReason,
            "goodId": self.goodId,
            #"goodNoteDetailStep": 3,
            "goodUrl": self.goodUrl,
            "userId": self.userId,
            "darenNoteTitle":self.darenNoteTitle,
        }

    def show_in_cmd(self):
        # 测试打印
        print('\n********* New Product **************')
        print('darenNoteCover:\t{}'.format(self.darenNoteCover))
        print('darenNotePubDate:\t{}'.format(self.darenNotePubDate))
        print('darenNoteReason:\t{}'.format(self.darenNoteReason))
        print('goodId:\t{}'.format(self.goodId))
        print('goodUrl:\t{}'.format(self.goodUrl))
        print('userId:\t{}'.format(self.userId))
        print('darenNoteTitle:\t{}'.format(self.darenNoteTitle))
        #print('createTime:\t{}'.format(self.createTime))


if __name__=="__main__":
    ProdPageParser(from_web=False).show_in_cmd()
