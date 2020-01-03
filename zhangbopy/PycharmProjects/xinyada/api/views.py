from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from rest_framework.views import APIView
from api.models import PicInfo
# Create your views here.
class indexView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("/home/wangzishen/PycharmProjects/xinyada/templates/index.html").read())

class analysisView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        # id
        # pic_name
        # pic_path
        # pic_type
        pic_name = data['pic_name']
        print(pic_name)
        pic_path = data['pic_path']
        print(pic_path)
        pic_id_list = []
        for name,path in zip(pic_name,pic_path):
            obj = PicInfo.objects.create(pic_name=name,pic_path=path,pic_type=4)
            pic_id_list.append(obj.id)
        inputparams = []
        url_dic = {}
        pic_url = []
        for path in pic_path:
            url = 'https://deepdraw-test.oss-cn-hangzhou.aliyuncs.com/' + path
            url_dic['pic_url'] = url
          #  inputparams.append(url_dic)
            pic_url.append(url)
        result_list = []
        for url in pic_url:
            url_dic['pic_url'] = url
            inputparams = [url_dic]
            input_dic = {
                            "action": "xinyada",
                            "inputparams": inputparams,
                            "model": "xinyada_model",
                            "proj": "deeplab",
                            "exec": "batch"
                        }
            import json
            input_json = json.dumps(input_dic)
            request_url = 'http://47.96.132.7:8083/polls/analyze_str/?str='+input_json
            print(request_url)
            import requests
            try:
                r = requests.get(request_url)
                #拿到返回json并反序列化为dic
            except:
                ret = {'code':1000,
                        'msg':'错误'}
            #return JsonResponse(ret)
            print(r.text)
            data = json.loads(r.text)
            result_list.append(data['predictions'][0]['type'])

            #遍历返还的4种结果
        id_card_list = []
        driver_license_list = []
        bank_card_list = []
        unsigned_list = []

        for result,url in zip(result_list,pic_url):
            if result == "id_card":
                id_card_list.append(url)
            elif result == "driver_license":
                driver_license_list.append(url)
            elif result == "bank_card":
                bank_card_list.append(url)
            else:
                unsigned_list.append(url)


        ret = {
            'code':'1001',
            'pic_id_list':pic_id_list,
            'input_json':input_json,
            'request_url':request_url,
            'result':{'id_card':id_card_list
                ,'driver_license':driver_license_list
                ,'bank_card':bank_card_list
                ,'unsigned':unsigned_list},
        }
        return JsonResponse(ret)


