#coding:utf-8
"""
@file:      ProductPageSpider
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-11-02 22:30
@description:
        本模块放django路由映射的视图函数
"""

from .SearchPageInfoGenerator import StoreInfoGenerator
from .ProductPageSpider import ProductPageSpider
from .func import json_response

@json_response
def get_store_info(request):
    ret = {'data': None, 'status': 0, 'message': None}
    if request.method != 'GET':
        ret['message'] = 'use GET method'
        return ret
    store_url = request.GET.get('store_url')
    print('receive store url: ',store_url)
    res = StoreInfoGenerator(store_url).to_json()
    print('merge result: ',res)
    if res not in [-1,-2]:
        ret['status'] = 1
        ret['data'] = res
    else:
        print('ret={}'.format(res))
        ret['status'] = res
        if res==-1:
            ret['message'] = 'Locate Error'
        else:
            ret['message'] = 'Merge Error'
    return ret

@json_response
def get_page_num(request):
    return handle_product_page_request(
            request,just_for_page_num=True)

@json_response
def get_products_info(request):
    return handle_product_page_request(
            request,just_for_page_num=False)

def handle_product_page_request(request,just_for_page_num=False):
    ret = {'data': None, 'status': 0, 'message': None}
    if request.method != 'GET':
        ret['message'] = 'use GET method'
        return ret
    products_url = request.GET.get('products_url')
    print('receive products_url: ',products_url)
    try:
        spider = ProductPageSpider(products_url)
        if just_for_page_num:
            ret['data'] = spider.get_page_num()
        else:
            ret['data'] = spider.get_products_info()
        ret['status'] = 1
        print('Sent info json ok!')
    except KeyError as e:
        ret['message'] = str(e)
    except Exception as e:
        ret['message'] = 'check products url'
        print(e)
    return ret