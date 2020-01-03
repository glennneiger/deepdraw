from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
import requests
import json


# Create your views here.
class RecogView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/recognition.html").read())


class FaceRecognition(APIView):
    def post(self, request, *args, **kwargs):
        try:
            print(request.data  )
            url = request.data['url']
            response = requests.get(
                'http://47.96.178.21:8088/hznz_framework/polls/analyze_str/?str={"action": "face", "inputparams": [{"pic_url": "' + url + '"}], "model": "default", "proj": "insightface", "exec": "online"}')
            body_response = json.loads(response.text)
            # print(json.loads(body_response.text)['date_str'])
            area_list = []
            for body in body_response["predictions"][0]:
                # print(body)
                w = body['r'] - body['l']
                h = body['b'] - body['t']
                area = w * h
                # print(area)
                area_list.append(area)
            max_index = area_list.index(max(area_list))
            body_info = body_response["predictions"][0][max_index]
            feature = body_response["predictions"][0][max_index]['feature']
            face_frame = {}
            face_frame['t'] = body_info['t']
            face_frame['r'] = body_info['r']
            face_frame['b'] = body_info['b']
            face_frame['l'] = body_info['l']
            # print(feature)
            import pymysql
            db = pymysql.connect(host='deepdraw-d2940b82.cn-shanghai-g.ads.aliyuncs.com', port=10017,
                                 user='LTAIHD1u5QVNgPdn', passwd='RLpRnudq5W3J85pZySIm90z4orKX83', db='deepdraw')
            cursor = db.cursor()
            sql = "select  ann_distance,  rowkey, attrs, url  from  ann(test_face,  feature,\'" + feature + "\', 50)"
            cursor.execute(sql)
            data = cursor.fetchall()
            url_list = []
            compare_face_frame = []
            for d in data:
                # print(json.loads(d[2]))
                # print('---------------------------')
                # print(header + d[2])
                url_list.append(d[3])
                compare_face_frame.append(
                    [json.loads(d[2])['t'], json.loads(d[2])['r'], json.loads(d[2])['b'], json.loads(d[2])['l']])
            # print(url_list)
            ret = {
                'code': 1,
                'result': '匹配成功',
                'main_face': face_frame,
                'url_list': url_list,
                'compare_face': compare_face_frame,
            }
        except Exception as e:
            print('--------error---------' + e)
            ret = {
                'code': 2,
                'result': '匹配失败',
            }
        return JsonResponse(ret)
