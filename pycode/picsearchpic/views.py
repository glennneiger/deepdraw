from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
import requests
import json
from string import digits


# Create your views here.
class ShowView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/soutunew.html").read())


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
            print(feature)
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



'''下面没有使用'''
class Get_Feature(APIView):
    def post(self, request, *args, **kwargs):
        try:
            import json
            import time
            print('datas',request.data)
            body_request_api_left='http://112.124.227.50:8088/hznz_framework/polls/analyze_str/?str='
            feature_request_api="http://60.191.84.99:5001/dml/?str="  #杭州2服务器
            annoy_request_api = "http://192.168.2.102:5001/dml_annoy/?str="
            # annoy_request_api = "http://192.168.2.102:5000/annoy/?str="
            word_request_api = "http://192.168.2.102:5000/word_search/?str="
            #searchpic_header = "http://47.102.104.13:8012/"

            start=time.time()
            url = request.data['url']
            print('urls', url)
            if len(url)>=50:
                body_request_api_right='{"action": "cloth", "inputparams": [{"pic_url": "' + url + '", "r": 1.0, "b": 1.0, "l": 0.0, "t": 0.0}], "model": "default", "proj": "yolov3", "exec": "online"}'
                body_request_api=body_request_api_left+body_request_api_right
                print('get',body_request_api)
                # .replace(".oss-cn-hangzhou.", ".oss-cn-hangzhou-internal.") 改成内网
                body_response = requests.get(body_request_api)
                print(body_response.text)
                body_response=eval(body_response.text)
                print('pre',body_response['predictions'])
                # print(json.loads(body_response.text)['date_str'])
                print('画box',time.time()-start)
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
                request_http = feature_request_api + request_str
                print('get',request_http)
                # 拼接请求向量地址
                info = request_http
                r = requests.get(info)
                feature_response = json.loads(r.text)
                feature = feature_response[0]['feature']
                print('feature', time.time() - start2)
                info = {
                    "feature": feature,
                    "num": 30  # 前24条相似数据
                }
                start3 = time.time()
                info = json.dumps(info)
                r = requests.get(annoy_request_api + info)
                print('get',annoy_request_api + info)
                # 拼接请求向量地址
                data_response = eval(r.text)
                data = data_response
                url_list = []
                word=''
                for d in data:
                    url_list.append(d['url'] + "@!400")
                    body_list.append(d['region'])
            else:
                word=url
                info = {
                    "word": word,
                    "num": 120  # 前24条相似数据
                }
                info = json.dumps(info)
                r = requests.get(word_request_api + info)
                print('get',word_request_api + info )
                # 拼接请求向量地址
                data_response = eval(r.text)
                data = data_response
                print('data', data)
                url_list = []
                body_list = []
                for d in data:
                    url_list.append(d['url'] + "@!400")
                    body_list.append(d['region'])
                body_info=''
            # print('请求', time.time() - start3)
            print('总用时', time.time() - start)
            print('word',word)
            print(url_list)
            ret = {
                'code': 1,
                'result': '匹配成功',
                'url_list': url_list,
                'body_info': body_info,
                'body_list': body_list,
                'name': word,
            }
        except Exception as e:
            print('--------error---------')
            print(e)
            ret = {
                'code': 2,
                'result': '后台匹配失败',
            }
        return JsonResponse(ret)


def test(request):
    return HttpResponse(content=open("./templates/demo1.html").read())

def test2(request):
    return HttpResponse(content=open("./templates/searchvue.html").read())

def test3(request):
    return HttpResponse(content=open("./templates/homepage.html").read())

class FeatureAndWord(APIView):
    def post(self, request, *args, **kwargs):
        try:
            import json
            import time
            print('aaa', request.data)
            word=request.data['searchs']
            print(word)
            # body_request_api_left='http://112.124.227.50:8088/hznz_framework/polls/analyze_str/?str='
            # feature_request_api="http://60.191.84.99:5001/dml/?str="
            # annoy_request_api = "http://192.168.2.102:5000/annoy/?str="
            # #searchpic_header = "http://47.102.104.13:8012/"
            word_request_api="http://192.168.2.102:5000/word_search/?str="

            info = {
                 "word": word,
                 "num": 24  # 前24条相似数据
            }
            info = json.dumps(info)
            r = requests.get(word_request_api + info)
            # 拼接请求向量地址
            data_response = eval(r.text)
            data = data_response
            print('data',data)
            url_list = []
            for d in data:
                url_list.append(d['url'] + "@!400")

            print(url_list)
            # start=time.time()
            # url = request.data['url']
            # body_request_api_right='{"action": "cloth", "inputparams": [{"pic_url": "' + url + '", "r": 1.0, "b": 1.0, "l": 0.0, "t": 0.0}], "model": "default", "proj": "yolov3", "exec": "online"}'
            # body_request_api=body_request_api_left+body_request_api_right
            # print(url)
            # body_response = requests.get(body_request_api)
            # print(body_response.text)
            # body_response=eval(body_response.text)
            # # print('pre',body_response['predictions'])
            # # print(json.loads(body_response.text)['date_str'])
            # print('画box',time.time()-start)
            # start2=time.time()
            # area_list = []
            # body_list=[]
            # for body in body_response["predictions"][0]:
            #     w = body['r'] - body['l']
            #     h = body['b'] - body['t']
            #     area = w * h
            #     # print(area)
            #     area_list.append(area)
            # max_index = area_list.index(max(area_list))
            # body_info = body_response["predictions"][0][max_index]
            # print('bodyinfo',body_info)
            # str = {
            #     "action": "feature",
            #     "inputparams": [
            #         {"pic_url": url,
            #          "r": body_info['r'], "b": body_info['b'], "l": body_info['l'], "t": body_info['t']}],
            #     "model": "default",
            #     "proj": "dml",
            #     "exec": "online"
            # }
            # request_str = json.dumps(str)
            # request_http = feature_request_api + request_str
            # # 拼接请求向量地址
            # info = request_http
            # r = requests.get(info)
            # feature_response = json.loads(r.text)
            # feature = feature_response[0]['feature']
            # print('feature', time.time() - start2)
            # info = {
            #     "feature": feature,
            #     "num": 24  # 前24条相似数据
            # }
            # start3 = time.time()
            # info = json.dumps(info)
            # r = requests.get(annoy_request_api + info)
            # # 拼接请求向量地址
            # data_response = eval(r.text)
            # data = data_response
            # url_list = []
            # for d in data:
            #     if d['dist'] <= 0.5:
            #         url_list.append(d['url'] + "@!400")
            #     else:
            #         pass
            # print('请求', time.time() - start3)
            # print('总用时', time.time() - start)


            ret = {
                'code': 1,
                'result': '匹配成功',
                'url_list': url_list,
                # 'body_info': body_info,
                # 'body_list': body_list,
            }
            HttpResponse(content=open("./templates/showpics.html").read())
            return render(request, 'showpics.html', {
                                                'url_list': url_list,
                                                 })
        except Exception as e:
            print('--------error---------')
            print(e)
            ret = {
                'code': 2,
                'result': '后台匹配失败',
            }
        return JsonResponse(ret)
