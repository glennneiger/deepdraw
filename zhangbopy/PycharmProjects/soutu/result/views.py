from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
import requests
import json


# Create your views here.
class ShowView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/show.html").read())


class GuideView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/head_link.html").read())


class Get_Feature(APIView):
    def post(self, request, *args, **kwargs):
        try:
            import json
            import time

            start=time.time()
            url = request.data['url']
            print(url)
            body_response = requests.get(
                'http://112.124.227.50:8088/hznz_framework/polls/analyze_str/?str={"action": "cloth", "inputparams": [{"pic_url": "' + url + '", "r": 1.0, "b": 1.0, "l": 0.0, "t": 0.0}], "model": "default", "proj": "yolov3", "exec": "online"}')
            print(body_response.text)
            # body_response = eval(body_response)
            body_response=eval(body_response.text)


            # print('pre',body_response['predictions'])
            # print(json.loads(body_response.text)['date_str'])
            print('box',time.time()-start)
            start2=time.time()
            area_list = []
            body_list=[]
            for body in body_response["predictions"][0]:
                w = body['r'] - body['l']
                h = body['b'] - body['t']
                area = w * h
                # print(area)
                area_list.append(area)
            max_index = area_list.index(max(area_list))
            body_info = body_response["predictions"][0][max_index]
            print('bodyinfo',body_info)
            str = {
                "action": "feature",
                "inputparams": [
                    {"pic_url": url,
                     "r": body_info['r'], "b": body_info['b'], "l": body_info['l'], "t": body_info['t']}],
                "model": "default",
                "proj": "dml",
                "exec": "online"
            }
            request_str = json.dumps(str)
            # print('reqs',request_str)
            # request_http = "http://112.124.227.50:8088/hznz_framework/polls/analyze_str/?str=" + request_str
            request_http="http://192.168.2.102:5001/dml/?str=" + request_str
            # print('request',request_http)
            info = request_http
            import json
            # info = json.dumps(info)
            r = requests.get(info)


            # feature_response = requests.get(request_http)
            feature_response = json.loads(r.text)
            # print(feature_response)
            # feature = feature_response['predictions'][0]['feature']
            feature = feature_response[0]['feature']
            print('feature',time.time()-start2)
            info = {
                "feature":feature,
                "num":24
            }

            # info = {
            #     "feature": "ejC/PJttCD4w/gy+V0kjvV2ZKbxDVg29Bo4qPrvH0zt+LjA+CG4RvRLFZzwPyGg93pfGPcH/Ub79vpS8zC09PjhOlz27Dr67lYioPkKyWT3ILxS+JkfmPVx9ory4lI4+hXV2PWbw4b1XwSI+UzQEPhh4gzz/xnO9DU3SPceRn70wgU2+BlQCvIstWz0Lc7a9SjZkvX3hj70nVIw9EamTPclfeb3syea9VLaEPl8JOL43+qM97OGAPlqTLL4YkCK+noqKPJxFPjwZIIq9pZF0vptSjbsc7RQ+lbpTO2XL/rxelh++BsitPShJUzxU2jW99QQjvoZpLL6AHZq8rwsjvg==",
            #     "num":20
            # }

            start3=time.time()
            root_url = "http://192.168.2.102:5000/annoy/?str="
            import json
            info = json.dumps(info)
            r = requests.get(root_url + info)
            data_response = eval(r.text)
            # print('res',data_response)
            data=data_response

            # import pymysql
            # db = pymysql.connect(host='deepdraw-d2940b82.cn-shanghai-g.ads.aliyuncs.com', port=10017,
            #                      user='LTAIHD1u5QVNgPdn', passwd='RLpRnudq5W3J85pZySIm90z4orKX83', db='deepdraw')
            # cursor = db.cursor()
            # sql = "select  ann_distance,  rowkey, local_path  from  ann(test_xj,  feature,\'" + feature + "\', 20)"
            # print(sql)
            # cursor.execute(sql)
            # data = cursor.fetchall()
            header = "http://192.168.2.102:8000/"
            url_list = []
            for d in data:

                body_dict = {}

                # print(type(d))
                # print(header + d['local_pic'])
                if d['dist'] <= 0.5:
                    # print('dddd', d['region'])
                    url_list.append(header + d['local_pic'])
                    body=eval(d['region'])

                    # print(body[:4])
                    body_dict['t']=body[0]
                    body_dict['r'] = body[1]
                    body_dict['b'] = body[2]
                    body_dict['l'] = body[3]
                    body_list.append(body_dict)
                else:
                    pass
            # print(url_list)
            print('body',body_list)
            print('请求',time.time()-start3)
            print('总用时',time.time()-start)
            ret = {
                'code': 1,
                'result': '匹配成功',
                'url_list': url_list,
                'body_info':body_info,
                'body_list':body_list,
            }
        except Exception as e:
            print('--------error---------' )
            print(e)
            ret = {
                'code': 2,
                'result': '匹配失败',
            }
        return JsonResponse(ret)
