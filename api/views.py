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
from static_spider.generate_daren_static_data import DarenStaticDataGenerator
from .SearchPageInfoGenerator import StoreInfoGenerator
from .ProductPageSpider import ProductPageSpider
from .DarenPageSpider import DarenPageSpider
from .mission9 import goodInfo
from .func import json_response,try_int
from .mission8 import ItemPageParser,UserRateInfoGenerator

@json_response
def get_store_info(request):
    ret = {'data': None, 'status': 0, 'message': None}
    if request.method != 'GET':
        ret['message'] = 'use GET method'
        return ret
    store_url = request.GET.get('store_url')
    print('receive store url: ',store_url)
    res = StoreInfoGenerator(store_url).to_json()
    #print('merge result: ',res)
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
        request,just_for_page_num=True
    )

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

@json_response
def get_daren_prods(request):
    ret = {'data': None, 'status': 0, 'message': None}
    if request.method != 'GET':
        ret['message'] = 'use GET method'
        return ret
    daren_url = request.GET.get('daren_url')
    print('receive daren home page url: ', daren_url)
    try:
        spider = DarenPageSpider(daren_url)
        ret['data'] = spider.to_json()
        ret['status'] = 1
        print('Sent info json ok!')
    except KeyError as e:
        ret['message'] = str(e)
    except Exception as e:
        ret['message'] = 'check daren page url,server except as [{}]'.format(str(e))
        print(e)
    return ret

@json_response
def get_daren_prods_plus(request):
    ret = {'data': None, 'status': 0, 'message': None}
    if request.method != 'GET':
        ret['message'] = 'use GET method'
        return ret
    daren_url = request.GET.get('daren_url')
    print('receive daren home page url: ', daren_url)
    try:
        spider = DarenPageSpider(daren_url)
        ret['data'] = spider.to_json()
        ret['status'] = 1
        print('Sent info json ok!')
    except KeyError as e:
        ret['message'] = str(e)
    except Exception as e:
        ret['message'] = 'check daren page url,server except as [{}]'.format(str(e))
        print(e)
    return ret

@json_response
def random_kick(request):
    return base_radom_kick(request,shuffle=False)


@json_response
def random_kick_plus(request):
    return base_radom_kick(request,shuffle=True)


def base_radom_kick(request,shuffle=False):
    ret = {'data': None, 'status': 0, 'message': None}
    if request.method != 'GET':
        ret['message'] = 'use GET method'
        return ret
    rq_dict = {
        'mysql': False,
        'thread_cot': 32,
        'dynamic_range_length': 1000,
        'save_db_type': 0,
        'err_print': 0,
        'use_proc_pool': 0,
        'use_email': 1,
        'debug': 0
    }
    for key in request.GET:
        rq_dict[key] = try_int(request.GET[key])
        #参数不全则用默认字典value
    if 'mysql' in rq_dict.keys() and rq_dict['mysql']==0:
        rq_dict['mysql'] = False
    else:
        rq_dict['mysql'] = True
    if 'dynamic_range_length' in rq_dict.keys() and \
            rq_dict['dynamic_range_length'] > 100000000:
        ret['message'] = 'dynamic_range_length need < 100000000'
        return ret
    try:
        generator = DarenStaticDataGenerator(
            start = rq_dict['start'],
            end = rq_dict['end']
        )
        generator.run(
            mysql=rq_dict['mysql'],
            thread_cot=rq_dict['thread_cot'],
            dynamic_range_length=rq_dict['dynamic_range_length'],
            save_db_type=rq_dict['save_db_type'],
            err_print=rq_dict['err_print'],
            visit_shuffle=shuffle,
            use_email=rq_dict['use_email'],
            use_proc_pool=rq_dict['use_proc_pool'],
            debug=rq_dict['debug']
        )
        ret['status'] = 1
        ret['message'] = 'run all range item ok'
    except Exception as e:
        ret['message'] = str(e)
    return ret

@json_response
def basic_prod_info(request):
    ret = {'data': None, 'status': 0, 'message': None}
    if request.method != 'GET':
        ret['message'] = 'use GET method'
        return ret
    default_info = {
        'prod_url': None,
        'good_id': None
    }
    for key in request.GET:
        default_info[key] = try_int(request.GET[key])
    for arg in [default_info['prod_url'],default_info['good_id']]:
        if arg==None:
            continue
        try:
            ret['data'] = goodInfo(arg).to_dict()
            ret['status'] = 1
            return ret
        except Exception as e:
            print(str(e))
            ret['message'] = str(e)
            continue
    return ret

@json_response
def basic_shop_info(request):
    ret = {'data': {}, 'status': 0, 'message': None}
    if request.method != 'GET':
        ret['message'] = 'use GET method'
        return ret
    kwargs = {
        'shop_id': None,
            #http://127.0.0.1:8000/basic_shop_info?shop_id=33121581
        'shop_url': None,
            #http://127.0.0.1:8000/basic_shop_info?shop_url=https://fishercoffee.taobao.com/
            #http://127.0.0.1:8000/basic_shop_info?shop_url=https://shop33121581.taobao.com/
        'item_url': None,
            #http://127.0.0.1:8000/basic_shop_info?item_url=https://item.taobao.com/item.htm?id=43167953945
        'item_id': None,
            #http://127.0.0.1:8000/basic_shop_info?item_id=43167953945
    }
    for key in request.GET:
        if key != 'cookie':
            kwargs[key] = request.GET[key]
    parser = ItemPageParser(**kwargs)
    #parser.print_html()
    ret['data']['rate_info'] = parser.get_rate_info()
    print(ret['data']['rate_info'] )
    info_engine = UserRateInfoGenerator(
        user_rate_id = parser.get_user_rate_id(),
        shop_id = parser.get_shop_id(),
        from_web = True,
        cookie= request.GET['cookie']
                if 'cookie' in request.GET.keys() else None
    )
    ret['data']['ShopService4_api'] = info_engine.get_ShopService4_api_json()
    refundIndex = info_engine.get_refundIndex_api_json()
    if refundIndex['success']:
        ret['data']['refundIndex_api'] = refundIndex
        #print(refundIndex['api_url'])
    ret['status'] = 1
    return ret