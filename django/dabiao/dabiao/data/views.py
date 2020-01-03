from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
import requests
import json
from string import digits
from data.models import Tripletmark
import pandas as pd
import numpy as np
import time
import random


# Create your views here.

class Test_Base(APIView):
    def get(self, request):
        print('ok');
        Tripletmark.objects.all().update(status='0')
        return HttpResponse('成功')


class testdb(APIView):
    def get(self, request):
        test1 = Tripletmark(uuid1='696b96b3afe941c089102c7702162f1d/original/30b9abaf33f34984857c8b95eb221216.jpg',
                            uuid2='9320b73325c24f859b2306c6165beaf5/original/5a61a9375fa74eadb80a44518c2e83c2.jpg',
                            bbox1='0.2167,0.7333,0.5144,0.3267', bbox2='0.4439,0.6208,0.7961,0.4325', mark='1', fix='0',
                            status='0')
        test1.save()
        return HttpResponse('成功')


class getAll(APIView):
    def get(self, request):
        test = Tripletmark.objects.all()
        print(test)
        for i in test:
            print(i.uuid1)
        return HttpResponse('success')


class LoginView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/login.html", ).read())


class IndexView(APIView):
    def post(self, request, *args, **kwargs):
        print(request.data);
        return HttpResponse(content=open("./templates/index.html").read())

    def get(self, request):
        return HttpResponse(content=open("./templates/index.html").read())


class GetTask(APIView):
    def get(self, request, *args, **kwargs):
        try:
            start1 = time.time()
            resData = list(Tripletmark.objects.filter(status='0')[0:100])
            start5 = time.time()
            print(start5 - start1, '查100')
            print(type(resData), len(resData))
            incomplete_task = random.sample(resData, 4)
            print('取4个', time.time() - start5)
            print('查询任务耗时:', time.time() - start1)
            allStatus = []
            # notSet = len(Tripletmark.objects.filter(status='0'))
            # alreadySuccess = len(Tripletmark.objects.filter(status='1'))
            # setNotSubmit = len(Tripletmark.objects.filter(status='2'))
            # notSubmit = notSet + setNotSubmit
            # print(notSet)
            start3 = time.time()
            print('查询状态耗时:', start3 - start1)
            allStatus.append(0)
            allStatus.append(0)
            allStatus.append(0)
            start4 = time.time()
            print('总耗时', start4 - start1)
            # print('还剩', notSubmit)
            if len(incomplete_task) != 0:
                ret = getTask(incomplete_task, allStatus)
                print('未分配id', ret['ids'])
                for i in ret['ids']:
                    Tripletmark.objects.filter(id=i).update(status='2')
            else:
                inpublished_task = Tripletmark.objects.filter(status='2').order_by('id')[0:4]
                if len(inpublished_task) != 0:
                    ret = getTask(inpublished_task, allStatus)
                    print('已分配未提交id', ret['ids'])
                else:
                    ret = {
                        "code": "3",
                        "msg": "任务全部完成",
                        'status': allStatus
                    }


        except Exception as e:
            ret = {
                "code": "2",
                "msg": "任务获取失败",
            }
            print('错误', e)
        return JsonResponse(ret)


class CheckLogin(APIView):
    def post(self, request, *args, **kwargs):
        try:
            print(request.data)
            if (request.data['name'] == 'root' and request.data['pwd'] == '123456'):
                ret = {
                    'code': '1',
                    'msg': '成功'
                }
            else:
                ret = {
                    'code': '0',
                    'msg': '用户名或密码错误'
                }
        except Exception as e:
            ret = {
                'code': '2',
                'msg': '失败'
            }
            print(e)
        return JsonResponse(ret)


class Submit(APIView):
    def post(self, request, *args, **kwargs):
        try:
            start = time.time()
            print(request.data)
            ids = request.data['ids']
            choose = request.data['choose']
            for i in range(len(ids)):
                print('现在', choose[i])
                Tripletmark.objects.filter(id=ids[i]).update(fix=choose[i])
                Tripletmark.objects.filter(id=ids[i]).update(status='1')
            ret = {
                'code': '1',
                'msg': '成功',
            }
            print('提交耗时', time.time() - start)

        except Exception as e:
            ret = {
                "code": "2",
                "msg": "任务获取失败",
            }
            print(e)
        return JsonResponse(ret)


def getUrls(uuid):
    url = 'http://47.96.222.66/url?uuid=' + uuid
    res = requests.get(url)
    dict_res = eval(res.text)
    return dict_res['result'][0] + '@!400'


def getTask(lists, allStatus):
    print('开始')
    urlsA = []
    urlsB = []
    boxesA = []
    boxesB = []
    ids = []
    for i in lists:
        print(i.id)
        urlsA.append(i.uuid1)
        urlsB.append(i.uuid2)
        boxesA.append(i.bbox1)
        boxesB.append(i.bbox2)
        ids.append(i.id)
    urlssA = []
    urlssB = []
    for j in range(len(urlsA)):
        single_urlA = urlsA[j]
        single_urlB = urlsB[j]
        resultA = getUrls(single_urlA)
        resultB = getUrls(single_urlB)
        urlssA.append(resultA)
        urlssB.append(resultB)
    print('urlssa', urlssA)
    print('urlssb', urlssB)
    ret = {
        "code": "1",
        "msg": '成功',
        'urlsA': urlssA,
        'urlsB': urlssB,
        'boxesA': boxesA,
        'boxesB': boxesB,
        'ids': ids,
        'static': allStatus,
    }
    return ret


class Count(APIView):
    def get(self, request, *args, **kwargs):
        try:
            print(request.data)
            ret = {
                'code': 1,
                'result': '写入成功',
            }
        except Exception as e:
            print(e)
            ret = {
                'code': '2',
                'msg': '写入失败',
                'result': e,
            }
        return JsonResponse(ret)


class Read_csv(APIView):
    def read_into_db(self, filename):
        db_data = pd.read_csv('/home/test/下载/' + filename)
        print(db_data.head())
        print(db_data[0:1], len(db_data))
        try:
            for i in range(0, len(db_data)):
                print(i)
                record = db_data[i:i + 1]
                record_list = np.array(record)
                data = record_list.tolist()
                uuid1 = str(data[0][1])
                uuid2 = str(data[0][2])
                bbox1 = str(data[0][3])
                bbox2 = str(data[0][4])
                mark = str(data[0][5])
                types = str(data[0][6])
                fix = '0'
                status = '0'
                # print(uuid1, uuid2, bbox1, bbox2, mark, fix, status)
                pic = Tripletmark(
                    uuid1=uuid1,
                    uuid2=uuid2,
                    bbox1=bbox1,
                    bbox2=bbox2,
                    mark=mark,
                    fix=fix,
                    status=status,
                    types=types,
                )
                pic.save()
                print('id', pic.id)
            ret = filename + '    load success'
        except Exception as e:
            ret = e
        return ret

    def post(self, request, *args, **kwargs):
        try:
            print(request.data['filename'])
            ret = self.read_into_db(request.data['filename'])
        except Exception as e:
            print(e)
            e = self.read_into_db(request.data['filename'])
            ret = {
                'code': '2',
                'msg': '写入失败',
                'result': e,
            }
        return HttpResponse(ret)

    def get(self, request, *args, **kwargs):
        try:
            print(request.data)
            # 获取body参数
            print(request.query_params)
            # 获取params参数
            ret = {
                'code': 1,
                'result': '写入成功',
            }
        except Exception as e:
            print(e)
            ret = {
                'code': '2',
                'msg': '写入失败',
                'result': e,
            }
        return HttpResponse(ret)
