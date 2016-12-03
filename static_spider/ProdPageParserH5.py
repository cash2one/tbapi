#coding:utf-8
"""
@file:      ProdPageParserH5
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm Mac
@create:    2016/12/3 19:10
@description:
            --
"""
import os,sys
sys.path.append(
    os.path.dirname(
        sys.path[0]
    )
)

import json
from api.decorators import except_return_none
from api.func import get_beijing_time

ERN_METHOD = lambda func:except_return_none(func,ModelName='ProdPageParser')

class ProdPageParserH5:
    '''
        sample url :
    '''
    def __init__(self,html=None,from_web=True):
        if not from_web:
            with open('prod_h5_sample.html','r') as f:
                html = f.read()
        #print(html)
        self.html = html
        txt = self.html.strip(' mtopjsonp1(')[:-1]
        print(txt)
        with open('./h5_txt','wb') as f:
            f.write(txt.encode('utf8'))
        self.jd = json.loads(txt)['data']
        print('json dict parsed ok')

    @property
    @ERN_METHOD
    def userId(self):
        return int(self.jd['account']['id'])

    @property
    @ERN_METHOD
    def darenNoteCover(self):
        return self.jd['feed']['groupProductInfo']['pics'][0]

    @property
    @ERN_METHOD
    def darenNotePubDate(self):
        return self.jd['feed']['timestamp']

    @property
    @ERN_METHOD
    def darenNoteReason(self):
        return self.jd['feed']['summary']

    @property
    @ERN_METHOD
    def goodId(self):
        return int(self.jd['feed']['id'])

    @property
    def goodUrl(self):
        return self.jd['feed']['groupProductInfo']['itemClickUrl']

    @property
    @ERN_METHOD
    def darenNoteTitle(self):
        return self.jd['feed']['title']

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

    def to_dict(self):
        if self.goodUrl==None:
            return {
                'bad_result': None
            }
        '''
        if self.darenNoteReason=='':
            print('--------- DeBug Info ----------')
            self.show_in_cmd()
        '''
        try:
            return {
                "darenNoteCover": self.darenNoteCover,
                "darenNotePubDate": self.darenNotePubDate,
                "darenNoteReason": self.darenNoteReason,
                "goodId": self.goodId,
                "goodUrl": self.goodUrl,
                "userId": self.userId,
                "darenNoteTitle":self.darenNoteTitle,
            }
        except:
            print('--------- Error Info ----------')
            self.show_in_cmd()

if __name__=="__main__":
    parser = ProdPageParserH5(from_web=False)
    print(parser.jd)
    parser.show_in_cmd()
