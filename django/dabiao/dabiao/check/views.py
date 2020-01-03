from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
import pandas as pd
import numpy as np
from check.models import CheckPics


# Create your views here.

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
        db_data = pd.read_csv(filename)
        current_class_id = 0
        try:
            for i in range(0, len(db_data)):
                record = db_data[i:i + 1]
                record_list = np.array(record)
                data = record_list.tolist()
                uuid = str(data[0][0])
                bbox = str(data[0][1])
                mark = str(data[0][2])
                fix = str(data[0][3])
                status = str(data[0][4])
                choice = str(data[0][5])
                print(uuid, bbox, mark, fix, status, choice)
                pic = CheckPics(
                    uuid=uuid,
                    bbox=bbox,
                    mark=mark,
                    fix=fix,
                    status=status,
                    choice=choice
                )
                pic.save()
                print(pic.id)
            ret = filename + '    load success'
        except Exception as e:
            ret = e
        return ret

    def post(self, request, *args, **kwargs):
        try:
            print(request.data['filename'])
            ret = self.read_into_db(request.data['filename'])
            ret = {
                'code': 1,
                'result': '写入成功',
            }
        except Exception as e:
            print(e)
            e = self.read_into_db(request.data['filename'])
            ret = {
                'code': '2',
                'msg': '写入失败',
                'result': e,
            }
        return JsonResponse(ret)

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
