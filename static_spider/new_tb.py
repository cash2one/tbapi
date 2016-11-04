#coding:utf-8
"""
@file:      tb_huodong_parser
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm Mac
@create:    2016/11/4 21:49
@description:
        sample url:
"""

import json,requests
from bs4 import BeautifulSoup

global error_prods

error_prods = []

def get_all_category_album_urls():
    url = 'https://tce.taobao.com/api/mget.htm?callback=jsonp119&tce_sid=1029158,1043874&tce_vid=6,0&tid=,&tab=,&topic=,&count=,&env=online,online&abs_mod_id=1626783544,4540445738'
    json_str = requests.get(url).text
    for spl_word in ['\n', '\t', '\r']:
        json_str = json_str.replace(spl_word, '')
    json_str = json_str.strip('window.jsonp119&&jsonp119(')[:-1]
    jd = json.loads(json_str)
    url_items = []
    for page in jd['result']['1029158']['result']:
        cgId = page['categoryId']
        cgName = page['categoryName']
        for custom in page['custom_custom']:
            url = 'https://tce.taobao.com/api/mget.htm?callback=jsonp449&tce_sid=1029264&tce_vid=9&tid=&tab=&topic=&count=&env=online&categoryId={}&albumId={}' \
                .format(cgId, custom['albumId'])
            item = [url,cgId,custom['albumId'],custom['albumName'],cgName]
            url_items.append(item)
            print(item)
            print('*********')
        print('--------')
    return url_items


def get_page_prods_info(page_txt):
    for spl_word in ['\n', '\t', '\r']:
        page_txt = page_txt.replace(spl_word, '')
    json_str = page_txt.strip('window.jsonp449&&jsonp449(')[:-1]
    jd = json.loads(json_str)
    prod_items = []
    for item in jd['result']['1029264']['result']:
        infoli = item['trackinfo'].split(':')
        detail_url = 'http://uz.taobao.com/detail/{}'.format(infoli[3][2:])
        item['detail_url'] = detail_url
        prod_items.append(item)
        print(item)
        print('---------')
    return prod_items


def get_user_id_in_detail_page(url):
    resp = requests.get(url)
    if resp.status_code==404:
        raise ConnectionError('404')
    html_source = resp.text
    try:
        soup = BeautifulSoup(html_source, 'lxml')
    except:
        soup = BeautifulSoup(html_source, 'html.parser')
    return int(soup.select_one('.avatar-wrap')['href'].split('/')[-2])

def crawl_per_prod_page(prod):
    print('抓取商品: {} {}'.format(prod['title'],prod['detail_url']))
    try:
        prod['user_id'] = get_user_id_in_detail_page(
            url=prod['detail_url'])
    except ConnectionError:
        print('404 error url: {} , {}'.format(prod['detail_url'],prod['title']))
        error_prods.append(prod)

def save_to_json_file(data,file_name):
    json_str = json.dumps(data)
    f = open(file_name,'w')
    f.write(json_str)
    f.close()


if __name__=='__main__':
    from multiprocessing.dummy import Pool as ThreadPool

    json_datas = []

    for item in get_all_category_album_urls():
        page_data = {'prods_list':None,'album_name':item[3],'category_name':item[-1]}
        url = item[0]
        category_id = item[1]
        alid = item[2]
        for i in range(5):
            prods_page_txt = requests.get(url).text
            try:
                page_prods = get_page_prods_info(prods_page_txt)
                break
            except:
                pass
        pool = ThreadPool(16)
        pool.map(crawl_per_prod_page,page_prods)
        pool.close()
        pool.join()
        page_data['prods_list'] = page_prods
        print(page_prods)
        json_datas.append(page_data)

    print('全部完成,存入 prods.json...')

    save_to_json_file(json_datas,'./prod.json')

    save_to_json_file(error_prods,'./err.json')