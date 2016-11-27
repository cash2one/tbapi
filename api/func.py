#coding:utf-8
import json,datetime,time

try:
    from django.http.response import HttpResponse
except:
    pass

class Timer:
    def __init__(self):
        self.start_ok = False

    def start(self):
        self.st = time.time()
        self.start_ok = True

    def end(self):
        if not self.start_ok:
            raise Exception('[Error] in Timer: Please run start() first.')
        self.gap = round(time.time()-self.st,2)

class CJsonEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj,datetime.datetime):
            return obj.strftime( '%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime( "%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self,obj)


def json_response(func):
    """
    A decorator thats takes a view response and turns it
    into json. If a callback is added through GET or POST
    the response is JSONP.
    """
    def decorator(request, *args, **kwargs):
        tm = Timer()
        tm.start()
        objects = func(request, *args, **kwargs)
        tm.end()
        print('Response time: {} s\n'.format(tm.gap))
        if isinstance(objects, HttpResponse):
            return object#服务端不希望返回jsonp的情况
        try:
            data = json.dumps(objects,cls=CJsonEncoder)
            if 'callback' in request.GET or 'callback' in request.POST:
                #给跨域的jsonp response!
                data = '%s(%s);' % (request.REQUEST['callback'], data)
                return HttpResponse(data, "text/javascript")
        except Exception as e:
            #服务端希望返回jsonp，但因为故障，不得不妥协成传string
            print('json_response error:',str(e))
            object['status'] = 2
            object['message'] = 'json_response() error, your got one string type'
            data = json.dumps(str(objects))
        return HttpResponse(data)#这里是返回给我的环境
    return decorator

from datetime import datetime, timedelta, timezone
def get_beijing_time(format='%Y-%m-%d %H:%M:%S'):
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(timezone(timedelta(hours=8))) \
        .strftime(format)

import requests
def request_with_ipad(url,time_out=15):
    for i in range(3):
        try:
            return requests.get(url,timeout=time_out,
                headers={'user-agent': 'Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5")'}
            )
        except Exception as e:
            print(str(e))
            pass

def get_item_dicts(json_str):
    item_dicts = []
    for prod in json_str.split('}, {'):
        # print(prod)
        jd = {}
        for kv in prod.split(', '):
            # print(kv)
            k = kv.split('=')[0].strip().strip('[{')
            try:
                v = kv.split('=')[1].strip().strip('}]')
            except:
                continue
            if '\r' in v or '[' in v:
                continue
            if v in ['{','}','[',']']:
                continue
            if v == 'null':
                v = None
            try:
                v = int(v)
            except:
                pass
            jd[k] = v
        # print(jd)
        item_dicts.append(jd)
    return item_dicts

def try_int(val):
    try:
        return int(val)
    except:
        return val
