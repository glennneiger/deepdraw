from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from dabiao.models import Mark_Pic, Get_Task
import pandas as pd
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

# ---------------------------设置模板路由---------------------------

class IndexView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/index.html").read())


class LoginView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/login.html").read())


class GetTask(APIView):
    # @csrf_exempt
    # def test(request):
    #     test = request.POST.get('test', '')
    #     return HttpResponse(test)
    def post(self, request, *args, **kwargs):
        # 得到人员信息
        data = request.data
        print('data', data)
        user_name = data['user_name']
        print(user_name)
        main_url_list = []
        compare_url_list = []
        task_id_list = []
        # if request.method == 'POST':
        try:
            # 查询该人员是否有未提交任务，若有，发布未完成任务
            incomplete_task = Get_Task.objects.filter(status=1)
            incomplete_task = incomplete_task.filter(user=user_name)
            if len(incomplete_task) != 0:  # 若有未提交任务
                tasks = Get_Task.objects.filter(status=1)
                task_id = tasks[0].class_id
                # tasks = tasks.filter(class_id=task_id)
                # update_data = {'status': 1, 'user': user_name}
                # tasks.update(**update_data)
                task_record = Mark_Pic.objects.filter(class_id=task_id)
                main_pic = task_record.filter(isMain=1)
                main_url_list.append({main_pic[0].url: [main_pic[0].t, main_pic[0].r, main_pic[0].b, main_pic[0].l]})
                compare_pic = task_record.filter(class_id=task_id)
                compare_pic = compare_pic.filter(isMain=0).order_by('-value')
                for pic in compare_pic:
                    print(pic.id)
                    task_id_list.append(pic.id)
                    compare_url_list.append({pic.url: [pic.t, pic.r, pic.b, pic.l]})
            else:  # 新发布任务,前端需要传入user_name标识任务
                tasks = Get_Task.objects.filter(status=0)
                task_id = tasks[0].class_id
                tasks = tasks.filter(class_id=task_id)
                update_data = {'status': 1, 'user': user_name}
                tasks.update(**update_data)
                task_record = Mark_Pic.objects.filter(class_id=task_id)
                main_pic = task_record.filter(isMain=1)
                main_url_list.append({main_pic[0].url: [main_pic[0].t, main_pic[0].r, main_pic[0].b, main_pic[0].l]})
                compare_pic = task_record.filter(class_id=task_id)
                compare_pic = compare_pic.filter(isMain=0)
                for pic in compare_pic:
                    task_id_list.append(pic.id)
                    compare_url_list.append({pic.url: [pic.t, pic.r, pic.b, pic.l]})
                    print(len(compare_url_list))
            ret = {
                "code": "1",
                "msg": "获取人物成功",
                "main_pic": main_url_list,
                "compare_pic": compare_url_list,
                "task_id": task_id_list,
                "class_id": task_id,
            }

        except Exception as e:
            ret = {
                "code": "2",
                "msg": "任务获取失败",
            }
            print(e)
        return JsonResponse(ret)


class Submit_Task(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        # user_name = data['user_name']
        # status_list = data['status_list']
        similar_pics = data['similar_pics']
        not_similar = data['not_similar']
        undefined = data['undefined']
        class_id = data['class_id']
        print(data)
        # 更新Mark_Pic中的数据
        try:
            for id in similar_pics:
                Mark_Pic.objects.filter(id=id).update(status=1)
            for id in not_similar:
                Mark_Pic.objects.filter(id=id).update(status=2)
            for id in undefined:
                Mark_Pic.objects.filter(id=id).update(status=3)
            # 更新GetTask表
            Get_Task.objects.filter(class_id=class_id).update(status=2)
            ret = {
                'code': 1,
                'msg': '提交成功'
            }
        except:
            ret = {
                'code': 1000,
                'msg': '提交失败'
            }
        return JsonResponse(ret)


class Read_csv(APIView):
    def read_into_db(self, filename):
        import pandas as pd
        import numpy as np
        db_data = pd.read_csv(filename)
        current_class_id = 0
        try:
            for i in range(0, len(db_data)):
                record = db_data[i:i + 1]
                record_list = np.array(record)
                data = record_list.tolist()
                url = str(data[0][0])
                class_id = int(data[0][1])
                t = float(data[0][2])
                r = float(data[0][3])
                b = float(data[0][4])
                l = float(data[0][5])
                value = float(data[0][6])
                isMain = int(data[0][7])
                status = int(data[0][8])
                pic = Mark_Pic(
                    url=url,
                    class_id=class_id,
                    t=t,
                    r=r,
                    b=b,
                    l=l,
                    value=value,
                    isMain=isMain,
                    status=status
                )
                pic.save()
                print(pic.id)
                if (class_id != current_class_id or current_class_id == 0):
                    task = Get_Task(
                        class_id=class_id,
                        status=status,
                        user='null',
                    )
                    task.save()
                    current_class_id = class_id
            ret = filename + '    load success'
        except Exception as e:
            ret = e
        return ret

    def post(self, request, *args, **kwargs):
        try:
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
