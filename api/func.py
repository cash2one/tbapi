#coding:utf-8
import json,datetime
from django.http.response import HttpResponse
# from sae.ext.storage import monkey
# from sae.storage import Bucket
# monkey.patch_all()


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
        data = None
        objects = func(request, *args, **kwargs)
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

#
# def read_spider_log():
#     bucket = Bucket('visualspider')
#     #print bucket.generate_url('amount_log.txt')
#     cnt = bucket.get_object_contents('amount_log.txt')
#     #print(cnt)
#     line_list = cnt.split('\n')
#     #print (line_list)
#     if line_list[0][-1]=='\r':
#         line_list = map(lambda x:x[:-1],line_list)
#         #print (line_list)
#     #fr = open('/s/visualspider/amount_log.txt','rb')
#     total_list = []
#     hour_delta_list = []
#     day_list = []
#     prev_hour = line_list[0].split(',')[1].split(' ')[1].split(':')[0]
#     prev_day = line_list[0].split(',')[1].split(' ')[0]
#     hour_amount = 0
#     day_amount = 0
#     for line in line_list:
#         print (day_amount)
#         #line = fr.readline()[:-1]#readline在sae中不可用
#         line_data = line.split(',')
#         #print(line_data)
#         if len(line_data)==1 or int(line_data[2])==0:
#             #delta为零是程序起始标志，此条目忽略
#             continue
#         ten_minute_delta = int(line_data[2])
#         day = line_data[1].split(' ')[0]
#         hour = line_data[1].split(' ')[1].split(':')[0]
#         if day != prev_day:
#             day_list.append([prev_day,day_amount,line_data[0]])
#             prev_day = day
#             day_amount = 0
#         else:
#             day_amount += ten_minute_delta
#         if hour != prev_hour:
#             prev_hour = hour
#             line_data[1] = time_str_convert(line_data[1])
#             hour_delta_list.append([line_data[1],hour_amount])
#             hour_amount = 0
#         else:
#             #print(line_data[2],hour_amount)
#             #print(line_data)
#             hour_amount += ten_minute_delta
#         total_list.append(line_data[:-1])
#     day_list.append([day,day_amount,line_list[-2].split(',')[0]])
#     # print(total_list)
#     # print(delta_list)
#     print (day_list)
#     return {'total_list':total_list,'delta_list':hour_delta_list,'day_list':day_list}
#
#
# def time_str_convert(time_str):
#     time_list = time_str_convert_list(time_str)
#     return time_list_convert_str(time_list)
#
#
# def time_str_convert_list(time_str):
#     #time_str形如2016-08-06 19:26:01
#     #转为[2016, 8, 6, 19, 26, 1]
#     date = time_str.split(' ')[0]
#     time = time_str.split(' ')[1]
#     time_info_list = date.split('-')
#     time_info_list.extend(time.split(':'))
#     return time_info_list
#
#
# def time_list_convert_str(time_list):
#     monthNames = [
#       "January", "February", "March",
#       "April", "May", "June", "July",
#       "August", "September", "October",
#       "November", "December"
#     ]
#     month = monthNames[int(time_list[1])-1]
#     time_str = ':'.join(time_list[3:])
#     year = time_list[0]
#     day = time_list[2]
#     date_str = month + ' ' + str(day) + ',' + str(year)
#     #print(date_str,time_str)
#     return date_str+' '+time_str


