

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from rest_framework.views import APIView
from xinyada.models import PicInfo
import shutil,rarfile,zipfile,os,sys
import oss2
auth = oss2.Auth('LTAIDGyxdSloVIAu', 'WVOPeB83DdojWcfs3wF6X6Ry0XNZYU')
# Endpoint以杭州为例，其它Region请按实际情况填写。
bucket = oss2.Bucket(auth, 'oss-cn-shanghai-internal.aliyuncs.com', 'deepdraw-zip')
# Create your views here.
def get_uuid():
    import uuid
    return str(uuid.uuid1())

class indexView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/xinyada.html").read())

class index_v2_View(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/xinyada_v1.html").read())

class analysisView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        # id
        # pic_name
        # pic_path
        # pic_type
        id_card_list = []
        driver_license_list = []
        driving_license_list = []
        bank_card_list = []
        unsigned_list = []

        pic_name = data['pic_name']
        print(pic_name)
        pic_path = data['pic_path']
        print(pic_path)
        print(len(pic_path))
        for i in range(len(pic_path)):
            if pic_path[i].split('.')[-1] == 'zip' or pic_path[i].split('.')[-1] == 'rar' or pic_path[i].split('.')[-1] == 'gz':
                import oss2
                #ret = oss_rename(user_id, org_pic)
                auth = oss2.Auth('LTAIDGyxdSloVIAu', 'WVOPeB83DdojWcfs3wF6X6Ry0XNZYU')
                # Endpoint以杭州为例，其它Region请按实际情况填写。
                bucket = oss2.Bucket(auth, 'http://oss-cn-hangzhou.aliyuncs.com', 'deepdraw-test')
                if pic_path[i].split('.')[-1] == 'zip':
                    bucket.get_object_to_file(pic_path[i], 'pic.zip')
                    z = zipfile.ZipFile('pic.zip', 'r')
                    z.extractall(path=r"/root/deepdraw/untitled/xinyada/zip_pic")
                    z.close()
                elif pic_path[i].split('.')[-1] == 'rar':
                    print("file type is RAR")
                dir_list = os.listdir("/root/deepdraw/untitled/xinyada/zip_pic")
                zip_pic_name = []
                zip_pic_path = []
                for name in dir_list:
                    if name.split('.')[-1] == 'jpeg' or name.split('.')[-1] == 'jpg' or name.split('.')[-1] == 'png':
                        zip_pic_name.append(name)
                        uuid = get_uuid()
                        path = 'xinyada/zip/' + uuid + name.split('.')[-1]
                        zip_pic_path .append(path)
                #解压后遍历上传图片
                #for path,name in zip(zip_pic_path,zip_pic_name):
                 #   bucket.put_object_from_file(path, "/root/deepdraw/untitled/xinyada/zip_pic/" + name ) 
                ret = {'code':1003,
                       'msg':'暂时不支持.zip/.rar/tar.gz等文件压缩包',
                       'pmeic_id_list':[],
                     # 'input_json':input_json,
                    #  'request_url':request_url,
                       'result':{
                                 'id_card':id_card_list,
                                 'driving_license':driving_license_list,
                                 'driver_license':driver_license_list,
                                 'bank_card':bank_card_list,
                                 'unsigned':unsigned_list,
                                 },
                       'pic_path':zip_pic_path,
                       'pic_name':zip_pic_name,
                       }
                return JsonResponse(ret) 

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
                        'msg':'模型请求错误',
		#	'model':r.text
                      }
            	#return JsonResponse(ret)
            print(r.text)
            data = json.loads(r.text)
            result_list.append(data['predictions'][0]['type'])

            #遍历返还的4种结果
#        id_card_list = []
 #       driver_license_list = []
  #      bank_card_list = []
   #     unsigned_list = []

        for result,url in zip(result_list,pic_url):
            if result == "id_card":
                id_card_list.append(url)
            elif result == "driving_license":
                driving_license_list.append(url)
            elif result == "driver_license":
                driver_license_list.append(url)
            elif result == "bank_card":
                bank_card_list.append(url)
            else:
                unsigned_list.append(url)


        ret = {
            'code':'1001',
	    'msg':'分析成功',
            'pic_id_list':pic_id_list,
            'input_json':input_json,
            'request_url':request_url,
            'result':{'id_card':id_card_list
                ,'driving_license':driving_license_list
                ,'driver_license':driver_license_list
                ,'bank_card':bank_card_list
                ,'unsigned':unsigned_list},
        }
        return JsonResponse(ret)



class analysis_v2_View(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        # id
        # pic_name
        # pic_path
        # pic_type
        id_card_list = []
        driver_license_list = []
        driving_license_list = []
        bank_card_list = []
        unsigned_list = []

        file_name = data['pic_name']
        print(file_name)
        file_path = data['pic_path']
        print(file_path)
        print(len(file_path))

        zip_file_list = []
        pic_file_list = []

        def check_file_type(file_path):
            for i in range(len(file_path)):
                if file_path[i].split('.')[-1] == 'zip' or file_path[i].split('.')[-1] == 'rar' or file_path[i].split('.')[-1] == 'gz':
                    zip_file_list.append(file_path[i])
                elif file_path[i].split('.')[-1] == 'jpeg' or file_path[i].split('.')[-1] == 'jpg' or file_path[i].split('.')[-1] == 'png':
                    pic_file_list.append(file_path[i])
        check_file_type(file_path)

        for zip_file in zip_file_list:
            if zip_file.split('.')[-1] == 'zip':
                bucket.get_object_to_file(zip_file, 'pic.zip')
                z = zipfile.ZipFile('pic.zip', 'r')
                z.extractall(path=r"/root/deepdraw/untitled/xinyada/zip_pic")
                z.close()

            elif zip_file.split('.')[-1] == 'rar':

                bucket.get_object_to_file(zip_file, 'pic.rar')
                r = rarfile.RarFile('pic.rar')
                r.extractall("/root/deepdraw/untitled/xinyada/zip_pic")
                r.close()

            else:print("This File Can Not Suport!")

            dir_file_list = []
            zip_pic_path = '/root/deepdraw/untitled/xinyada/zip_pic/'
            def listdir(path, list_name):
                for file in os.listdir(path):
                    file_path = os.path.join(path, file)
                    if os.path.isdir(file_path):
                        listdir(file_path, list_name)
                    elif os.path.splitext(file_path)[1]=='.png'or os.path.splitext(file_path)[1]=='.jpg'or os.path.splitext(file_path)[1]=='.jpeg':
                        list_name.append(file_path)
                return list_name
            dir_file_list = listdir(zip_pic_path,dir_file_list)
            print(dir_file_list)
            pic_file_list = []
            for path in dir_file_list:
                if '__MACOSX/' not in path:
                    objname = 'xinyada_zip/'+get_uuid() +'.'+ path.split('.')[-1]
                    bucket.put_object_from_file(objname, path)
                    os.remove(path)
                    pic_file_list.append(objname)
            print('UPLOAD SUCCESS!')
        pic_url = []
        url_dic = {}
        result_list = []
        inputparams_list = []
        batch_size = 83
        mod = len(pic_file_list)%batch_size
        request_time = len(pic_file_list)//batch_size
        count = 0
        inputparams = []
        for path in pic_file_list:
            url = 'https://deepdraw-zip.oss-cn-shanghai.aliyuncs.com/' + path
            url_dic['pic_url'] = url
            inputparams.append(url_dic)
            url_dic = {}
            pic_url.append(url)
            if request_time == 0:
                if len(inputparams) == len(pic_file_list):
                    inputparams_list.append(inputparams)
                    inputparams = []
            elif count != request_time:
                if len(inputparams) == batch_size:
                    inputparams_list.append(inputparams)
                    count = count + 1
                    inputparams = []
            else:
                if len(inputparams)==mod:
                    inputparams_list.append(inputparams)
                    inputparams = []

        for inputparams in inputparams_list:
            input_dic = {
                            "action": "xinyada",
                            "inputparams": inputparams,
                            "model": "default",
                            "proj": "mobilenetv3",
                            "exec": "online"
                        }
            import json
            input_json = json.dumps(input_dic)
            #request_url = 'http://47.96.132.7:8083/polls/analyze_str/?str='+input_json
            request_url = 'http://47.96.178.21:8088/hznz_framework/polls/analyze_str/?str='+input_json
            print(request_url)
            import requests
            try:
                r = requests.get(request_url)
                #拿到返回json并反序列化为dic
            except:
                ret = {'code':1000,
                        'msg':'模型请求错误',
                #       'model':r.text
                      }
                #return JsonResponse(ret)
            print(r.text)
            data = json.loads(r.text)
            for re in data['predictions']:
                result_list.append(re['type'])
        for result,url in zip(result_list,pic_url):
            if result == "id_card":
                id_card_list.append(url)
            elif result == "driving_license":
                driving_license_list.append(url)
            elif result == "driver_license":
                driver_license_list.append(url)
            elif result == "bank_card":
                bank_card_list.append(url)
            else:
                unsigned_list.append(url)
 

        ret = {
               'code':'1001',
               'msg':'分析成功',
        #       'pic_id_list':pic_id_list,
               'input_json':input_json,
               'request_url':request_url,
               'result':{'id_card':id_card_list
                ,'driving_license':driving_license_list
                ,'driver_license':driver_license_list
                ,'bank_card':bank_card_list
                ,'unsigned':unsigned_list},
              }
        return JsonResponse(ret)

class analysis_v3_View(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        # id
        # pic_name
        # pic_path
        # pic_type
        id_card_list = []
        driver_license_list = []
        driving_license_list = []
        bank_card_list = []
        unsigned_list = []

        file_name = data['pic_name']
        print(file_name)
        file_path = data['pic_path']
        print(file_path)
        print(len(file_path))

        zip_file_list = []
        pic_file_list = []

        def check_file_type(file_path):
            for i in range(len(file_path)):
                if file_path[i].split('.')[-1] == 'zip' or file_path[i].split('.')[-1] == 'rar' or file_path[i].split('.')[-1] == 'gz':
                    zip_file_list.append(file_path[i])
                elif file_path[i].split('.')[-1] == 'jpeg' or file_path[i].split('.')[-1] == 'jpg' or file_path[i].split('.')[-1] == 'png':
                    pic_file_list.append(file_path[i])
        check_file_type(file_path)

        for zip_file in zip_file_list:
            if zip_file.split('.')[-1] == 'zip':
                bucket.get_object_to_file(zip_file, 'pic.zip')
                z = zipfile.ZipFile('pic.zip', 'r')
                z.extractall(path=r"/root/deepdraw/untitled/xinyada/zip_pic")
                z.close()

            elif zip_file.split('.')[-1] == 'rar':

                bucket.get_object_to_file(zip_file, 'pic.rar')
                r = rarfile.RarFile('pic.rar')
                r.extractall("/root/deepdraw/untitled/xinyada/zip_pic")
                r.close()

            else:print("This File Can Not Suport!")

            dir_file_list = []
            zip_pic_path = '/root/deepdraw/untitled/xinyada/zip_pic/'
            def listdir(path, list_name):
                for file in os.listdir(path):
                    file_path = os.path.join(path, file)
                    if os.path.isdir(file_path):
                        listdir(file_path, list_name)
                    elif os.path.splitext(file_path)[1]=='.png'or os.path.splitext(file_path)[1]=='.jpg'or os.path.splitext(file_path)[1]=='.jpeg':
                        list_name.append(file_path)
                return list_name
            dir_file_list = listdir(zip_pic_path,dir_file_list)
            print(dir_file_list)
            pic_file_list = []
            for path in dir_file_list:
                if '__MACOSX/' not in path:
                    objname = 'xinyada_zip/'+get_uuid() +'.'+ path.split('.')[-1]
                    bucket.put_object_from_file(objname, path)
                    os.remove(path)
                    pic_file_list.append(objname)
            print('UPLOAD SUCCESS!')
        pic_url = []
        url_dic = {}
        for path in pic_file_list:
            url = 'https://deepdraw-zip.oss-cn-shanghai.aliyuncs.com/' + path
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
                            "model": "default",
                            "proj": "mobilenetv3",
                            "exec": "online"
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
                        'msg':'模型请求错误',
                #       'model':r.text
                      }
                #return JsonResponse(ret)
            print(r.text)
            data = json.loads(r.text)
            result_list.append(data['predictions'][0]['type'])
        for result,url in zip(result_list,pic_url):
            if result == "id_card":
                id_card_list.append(url)
            elif result == "driving_license":
                driving_license_list.append(url)
            elif result == "driver_license":
                driver_license_list.append(url)
            elif result == "bank_card":
                bank_card_list.append(url)
            else:
                unsigned_list.append(url)


            ret = {
                   'code':'1001',
                   'msg':'分析成功',
        #           'pic_id_list':pic_id_list,
                   'input_json':input_json,
                   'request_url':request_url,
                   'result':{'id_card':id_card_list
                    ,'driving_license':driving_license_list
                    ,'driver_license':driver_license_list
                    ,'bank_card':bank_card_list
                    ,'unsigned':unsigned_list},
                  }
        return JsonResponse(ret)



















































