from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
import requests
import json
from string import digits


# Create your views here.
class ShowView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/show.html").read())

class TestView(APIView):
    def get(self,request):
        return HttpResponse(content=open("./templates/test.html").read())

class ShowVue(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/searchvue.html").read())


class GuideView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/head_link.html").read())

class Get_Box(APIView):
    def post(self, request,*args,**kwargs):
        print('图片url',request.data);
        try:
            print('开始获取box')
            import json
            import time
            body_list = []
            # print('data',request.data)
            url = request.data['url']
            word = ''
            print(len(url))
            if len(url) >= 50:
                body_request_api_left = 'http://112.124.227.50:8088/hznz_framework/polls/analyze_str/?str='
                body_request_api_right='{"action": "cloth", "inputparams": [{"pic_url": "' + url + '", "r": 1.0, "b": 1.0, "l": 0.0, "t": 0.0}], "model": "default", "proj": "yolov3", "exec": "online"}'
                body_request_api=body_request_api_left+body_request_api_right
                body_response = requests.get(body_request_api)
                body_response=eval(body_response.text)
                for body in body_response["predictions"][0]:
                    print('nowbody',body)
                    body_dict = {}
                    body_dict['t'] = body['t']
                    body_dict['r'] = body['r']
                    body_dict['b'] = body['b']
                    body_dict['l'] = body['l']
                    body_dict['type'] = body['type']
                    body_list.append(body_dict)
                body_info = body_list
                print('box个数',body_info)
            else:
                print('长度不够')

            print(body_info,body_list)
            ret = {
                'code': 1,
                'result': '匹配成功',
                'body_info': body_info,
                'body_list': body_list,
            }
        except Exception as e:
            print('--------error---------')
            print(e)
            ret = {
                'code': 2,
                'result': '后台匹配失败',
            }
        return JsonResponse(ret)


class Get_Urls(APIView):
    def post(self, request,*args,**kwargs):
        try:
            print('接受图片data', request.data)
            # feature_request_api="http://60.191.84.99:5001/dml/?str="
            feature_request_api = "http://192.168.2.102:5003/dml/?str="
            # annoy_request_api = "http://192.168.2.102:5000/annoy/?str="
            annoy_request_api = "http://192.168.2.102:5001/dml_annoy/?str="
            #word_request_api = "http://192.168.2.102:5000/word_search/?str="
            body_list=[]
            url = request.data['url']
            box = request.data['box']
            s = box[4]
            remove_digits = str.maketrans('', '', digits)
            res = s.translate(remove_digits)
            print("开始匹配")
            strs = {
                "action": "feature",
                "inputparams": [
                    {"pic_url": url,
                     "r": box[1],
                     "b": box[2],
                     "l": box[3],
                     "t": box[0],
                     }],
                "model": "default",
                "proj": "dml",
                "exec": "online"
            }
            request_str = json.dumps(strs)
            request_http = feature_request_api + request_str
            print('get请求向量', request_http)
            # 拼接请求向量地址
            info = request_http
            r = requests.get(info)
            feature_response = json.loads(r.text)
            feature = feature_response[0]['feature']
            info = {
                "feature": feature,
                "type" :res,
                "num": 20  # 前24条相似数据
            }
            info = json.dumps(info)
            r = requests.get(annoy_request_api + info)
            print('get匹配图片', annoy_request_api + info)
            # 拼接请求向量地址
            data_response = eval(r.text)
            data = data_response
            print('data',len(data))
            url_list = []
            dist_list = []
            click_url_list = []
            # word = ''
            for d in data:
                dists =round(d['dist'],2)
                dist_list.append(dists)
                click_url_list.append(d['product_url']);
                url_list.append(d['url'])
                body_list.append(d['region'])
            ret = {
                'code': 1,
                'result': '匹配成功',
                'url_list': url_list,
                'body_list': body_list,
                "dist_list":dist_list,
                "click_url_list":click_url_list,
            }
        except Exception as e:
            print('--------error---------')
            print(e)
            ret = {
                'code': 2,
                'result': '后台匹配失败',
            }

        return JsonResponse(ret)
