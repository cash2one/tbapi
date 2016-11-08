#coding:utf-8
"""
@file:      ActInfoGenerator
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm Mac
@create:    2016/11/8 21:06
@description:
        获取双十一活动页的活动标签和店铺信息
"""
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
import requests,re,json

public_sid_pool = []

def request_except(url):
    for i in range(5):
        try:
            return requests.get(url)
        except:
            pass

class ActInfoGenerator:
    def __init__(self):
        self.data = []

    def run(self):
        ext_pool = ThreadPool(4)
        ext_pool.map(self.crawl_prt_acttag,self.get_act_tags())
        ext_pool.close()
        ext_pool.join()

    def crawl_prt_acttag(self,act_tag):
        pool = ThreadPool(16)
        sub_tags = self.get_sub_tags(act_url=act_tag['url'])
        act_dict = {'area': act_tag, 'category':[] }
        act_sub_tags = [(act_tag, sub_tag, act_dict) for sub_tag in sub_tags]
        pool.map(self.crawl_per_subtag, act_sub_tags)
        pool.close()
        pool.join()
        self.data.append(act_dict)

    def crawl_per_subtag(self,act_sub_tag):
        sub_tag = act_sub_tag[1]
        act_tag = act_sub_tag[0]
        act_dict = act_sub_tag[2]
        print('------------------\n')
        print(sub_tag)
        if 'url' not in sub_tag.keys():
            return
        print('act_tag_url:{}\nsub_tag_url:{}' \
            .format(act_tag['url'], sub_tag['url']))
        if act_tag['url'] in sub_tag['url']:
            # 需要存在包含路由关系
            tces = self.get_page_tces(sub_url=sub_tag['url'])
        else:
            tces = []
        print(tces)
        shops = self.get_shops_by_sid_api(tces)
        unit = {'sub_tag': sub_tag, 'shops': shops}
        act_dict['category'].append(unit)

    def get_act_tags(self):
        #得到一级菜单
        html = open('1.html','rb').read()
        soup = BeautifulSoup(html, 'lxml')
        return [
            { 'url':a['href'],'name':a.text.strip() }
                for a in soup.select('.otherVenue')
        ]

    def get_sub_tags(self,act_url):
        #得到二级菜单
        soup  = BeautifulSoup(request_except(act_url).text,'lxml')
        try:
            json_str = soup.find('script', text=re.compile('"isHot"')).text
            json_str = re.split('globalData = |]};', json_str)[1] + ']}'
            return json.loads(json_str)['page_list'][0]['subpage_list']
        except Exception as e:
            #print(str(e))
            return []

    def get_page_tces(self,sub_url):
        #得到某页所有的tce端口信息
        print(sub_url)
        soup  = BeautifulSoup(request_except(sub_url).text,'lxml')
        json_strs = [ tce_script.text for tce_script in
            soup.find_all('script', text=re.compile('tce_sid'))
        ]
        page_sids = []
        for json_str in json_strs:
            #print('json_str: {}'.format(json_str))
            arr = json_str.split(';')
            #possible_indexs = [0,3]
            possible_indexs = [0,3]
            for index in possible_indexs:
                try:
                    arr[index]
                except:
                    break
                #print('index:{}'.format(index))
                try:
                    json_str = '{}'.format(
                        re.split("Data = ",arr[index])[1]
                    )
                    #print('json_str: {}'.format(json_str))
                except Exception as e:
                    pass
                    #print(str(e))
            item_sids = []
            for jd in json.loads(json_str):
                jd_sids = []
                for key in ['moduleDataSource','htmlList','nav','mainVenue','page_groups',\
                        'linkBtnData','skinData','tce_hotarea_pc']:
                    try:
                        tce_sid = jd['data'][key][0]['data_para']['tce_sid']
                        tce_vid = jd['data'][key][0]['data_para']['tce_vid']
                        jd_sids.append({'sid':tce_sid,'vid':tce_vid})
                    except:
                        continue
                #print('jd_sids:{}'.format(jd_sids))
                item_sids.extend(jd_sids)
            #print('item_sids:{}'.format(item_sids))
            page_sids.extend(item_sids)
        #print('page_sids:{}'.format(page_sids))
        return page_sids

    def get_shops_by_sid_api(self, tces):
        #带着tce信息集请求api
        if tces==[]:
            return []
        sid_str = 'tce_sid='
        vid_str = 'tce_vid='
        for tce in tces:
            '''
            if tce['sid'] in public_sid_pool:
                #去重复
                continue
            else:
                public_sid_pool.append(tce['sid'])
            '''
            sid_str += '{},'.format(tce['sid'])
            vid_str += '{},'.format(tce['vid'])
        sid_str = sid_str[:-1]
        vid_str = vid_str[:-1]
        url = 'https://tce.taobao.com/api/mget.htm?{}&{}' \
            .format(sid_str, vid_str)
        print(url)
        json_txt = request_except(url).text
        #print(json_txt)
        api_json = json.loads(json_txt)['result']
        shops = []
        for tce in tces:
            key = str(tce['sid'])
            if key not in api_json:
                continue
            for shop in api_json[key]['result']:
                #print(shop)
                if 'shop_activity_url' in shop.keys():
                    shops.append(shop)
        print('length:{}'.format(len(shops)))
        return shops

    def save_to_json_file(self,data, file_name):
        json_str = json.dumps(data)
        f = open(file_name, 'w')
        f.write(json_str)
        f.close()

    def to_list(self):
        self.run()
        self.save_to_json_file(data=self.data,file_name='./shop.json')
        return self.data


if __name__=="__main__":
    generator = ActInfoGenerator()
    '''
    generator.get_shops_by_sid_api(
        tces=[
            {'vid': '0', 'sid': 1081757}, {'vid': '22', 'sid': 1033965}, {'vid': '0', 'sid': 1034129},
            {'vid': '19', 'sid': 1034313}, {'vid': '7', 'sid': 1043896}
        ]
    )
    '''
    generator.to_list()