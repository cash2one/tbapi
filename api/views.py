from django.shortcuts import render

# Create your views here.

from .SearchPageInfoGenerator import StoreInfoGenerator
from .func import json_response

@json_response
def get_store_info(request):
    ret = {'data': None, 'status': 0, 'message': None}
    if request.method != 'GET':
        ret['message'] = 'use GET method'
        return ret
    store_url = request.GET.get('store_url')
    print('store url: ',store_url)
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