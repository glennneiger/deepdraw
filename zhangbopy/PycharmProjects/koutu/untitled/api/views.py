from django.shortcuts import render

# Create your views here.
import json,time
from random import randrange
from django.http import HttpResponse,JsonResponse
from rest_framework.views import APIView
from django.core import serializers
from pyecharts.charts import Bar
from pyecharts import options as opts
from django.forms.models import model_to_dict
from api.models import UserInfo,UserToken,TaskInfo,PicInfo
from retry import retry
import oss2,zipfile

# Create your views here.a

##########可视化拓展-------------------------------------------------------------------------

def response_as_json(data):
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str,
        content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, code=200):
    data = {
        "code": code,
        "msg": "success",
        "data": data,
    }
    return response_as_json(data)


def json_error(error_string="error", code=500, **kwargs):
    data = {
        "code": code,
        "msg": error_string,
        "data": {}
    }
    data.update(kwargs)
    return response_as_json(data)


myJsonResponse = json_response
JsonError = json_error


def bar_base() -> Bar:
    c = (
        Bar()
        .add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
        .add_yaxis("商家A", [randrange(0, 100) for _ in range(6)])
        .add_yaxis("商家B", [randrange(0, 100) for _ in range(6)])
        .set_global_opts(title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题"))
        .dump_options()
    )
    return c



class ChartView(APIView):
    def get(self, request, *args, **kwargs):
        return myJsonResponse(json.loads(bar_base()))

class VisualView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/echarts.html").read())

class IndexView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/index.html").read())

class Index_v2_View(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/index_v1.html").read())

class zjd_testView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/main_page_login.html").read())

class cssView(APIView):
    def get(self,request,*args, **kwargs):
        return HttpResponse(content=open("root/deepdraw/untitled/static/main_page_style.css").read())
class mtploadView(APIView):
    def get(self,request,*args, **kwargs):
        return HttpResponse(content=open("./templates/mtp_upload_page.html").read())

class phonelogView(APIView):
    def get(self,request,*args, **kwargs):
        return HttpResponse(content=open("./templates/phone_log_page.html").read())

class testView(APIView):
    def get(self,request,*args, **kwargs):
        return HttpResponse(content=open("./templates/mtp_upload_page_v2.html").read())

###########------------------------------------------------------------------------------------

###########短信验证码----------------------------------------------------------------------------
class MsgView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        Phone = data['Phone']
        code = get_random_code(len = 6)
        msg = {"code":code}

        from aliyunsdkcore.client import AcsClient
        from aliyunsdkcore.request import CommonRequest
        client = AcsClient('LTAINoeFiTtb5Ldh', 'FxOZ9pfmLB9LwIBABsauu8Md8dJjn7', 'cn-hangzhou')

        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('http')  # https | http
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('RegionId', "cn-hangzhou")
        request.add_query_param('PhoneNumbers', Phone)
        request.add_query_param('SignName', "DeepDraw深绘智能")
        request.add_query_param('TemplateCode', "SMS_170346491")
        request.add_query_param('TemplateParam', str(msg))

        response = client.do_action(request)
        # print(str(response, encoding='utf-8'))
        # python2:  print(response)
        
        test_obj = UserInfo.objects.filter(user_name=data['Phone']).first()
       # if not test_obj:
        if not test_obj:
            obj = UserInfo.objects.create(user_name=Phone,
                                          user_type=1,
                                          user_detil='',
                                          password=code,
                                          )

        else:
            UserInfo.objects.filter(user_name=Phone).update(user_name=Phone,password=code) 
            obj = UserInfo.objects.filter(user_name=Phone).first()
        token = get_tocken()
        try:
                    # 存在就更新，不存在就创建
            UserToken.objects.update_or_create(user=obj,defaults={'token':token})
        except:
            ret = {'code': 1002,
                   'msg': 'token保存失败',
                  }
        #result = {#'user_name':obj.user_name,
                  #'user_type':obj.user_type,
                  #'user_detil':obj.user_detil,
         #         'user_id':obj.id}

        ret = {'code':1001,
               'msg':'获取验证码成功',
               'random_code':code,
               #'token':token,
               'user_id':obj.id,
               }

        return JsonResponse(ret)

###########------------------------------------------------------------------------------------


###########用户验证-----------------------------------------------------------------------------

class SignupView(APIView):
    '''
    用于用户注册
    '''
    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            obj = UserInfo.objects.create(user_name=data['user_name'],
                                          user_type=data['user_type'],
                                          user_detil=data['user_detil'],
                                          password=data['password']
                                          )

            result = {'user_name': obj.user_name,
                      'user_type': obj.user_type,
                      'user_detil': obj.user_detil,
                      'id': obj.id}

            ret = {'code': 1001,
                   'msg': '注册成功',
                   'result':result,
                   'token': get_tocken()}

        except Exception as e:
            ret = {'code':1000,
                   'msg':'注册失败'}

        return JsonResponse(ret)

class LoginView(APIView):

    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/echarts.html").read())

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            obj = UserInfo.objects.filter(user_name=data['user_name'],
                                          password=data['password']).first()
            if not obj:
                ret = {'code': 1000,
                       'msg': '认证失败',
                       }
            else:

                #认证通过返回token
                token = get_tocken()
                #重置密码
                UserInfo.objects.filter(user_name=data['user_name'],
                                          password=data['password']).update(password='deepdraw_wzs')
                result = {'user_name':obj.user_name,
                          'user_type':obj.user_type,
                          'user_detil':obj.user_detil,
                          'id':obj.id}
                ret = {'code': 1001,
                       'msg': '登录成功',
                       'result':result,
                       'token': token}
                try:
                    # 存在就更新，不存在就创建
                    UserToken.objects.update_or_create(user=obj,
                                                       defaults={'token':token})
                except:
                    ret = {'code': 1002,
                           'msg': 'token保存失败',
                           }
        except Exception as e:
            ret = {'code': 1003,
                   'msg': '请求异常',
                   }
        return JsonResponse(ret)



class Authentication(object):
    pass
################---------------------------------------------------------------------------------

################----------功能逻辑函数-------------------------------------------------------------

def image_md5(file_name):
    import hashlib
    image_file = open(file_name,'rb').read()
    feat_hash = hashlib.md5(image_file).hexdigest()
    return  feat_hash

def oss_obj_name(user_id,file_name):
    md5 = image_md5(file_name)
    obj_name = 'output_folder/'+ user_id + '/pic/'+md5[:2]+'/'+md5 +'.png'
    return  obj_name

def oss_sdk(user_id,url_list,org_pic):
    print('user_id:'+user_id)
    print(url_list)
    from removebg import RemoveBg
    import oss2

    rmbg_url_list = []
    for source in org_pic:
 # 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
        auth = oss2.Auth('LTAI4VIH8rP2cjtg', 'uzXZC3TB4egoT5FZe0nYn1BsoqXo5x')
        # Endpoint以杭州为例，其它Region请按实际情况填写。
        bucket = oss2.Bucket(auth, 'http://oss-cn-hangzhou.aliyuncs.com', 'deepdraw-test')

        image_name = 'oss.'+source_obj.split('.')[-1]
        bucket.get_object_to_file(source_obj, image_name)
        print('--------------------------rmbg:url'+url) 
        ##模型接口
        rmbg = RemoveBg("swJYPyjfZsAcLnZYDqNR4ckM", "error.log")
        rmbg.remove_background_from_img_file(image_name)
        
    
        # 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
        auth = oss2.Auth('LTAI4VIH8rP2cjtg', 'uzXZC3TB4egoT5FZe0nYn1BsoqXo5x')
        # Endpoint以杭州为例，其它Region请按实际情况填写。
        bucket = oss2.Bucket(auth, 'http://oss-cn-hangzhou.aliyuncs.com', 'deepdraw-test')

        file_name = '/root/deepdraw/untitled/api/no-bg.png'
        # <yourLocalFile>由本地文件路径加文件名包括后缀组成，例如/users/local/myfile.txt
        
        new_url = 'https://deepdraw-test.oss-cn-hangzhou.aliyuncs.com/'+oss_obj_name(user_id,file_name)
        bucket.put_object_from_file(oss_obj_name(user_id,file_name), file_name)
        rmbg_url_list.append(new_url)
        print('new_url:'+new_url)
        ret = {'code': 1001,
               'msg': '上传成功',
               }
    return rmbg_url_list
    



def oss_rename(user_id,org_pic):
    import oss2

    auth = oss2.Auth('LTAI4VIH8rP2cjtg', 'uzXZC3TB4egoT5FZe0nYn1BsoqXo5x')
    # Endpoint以杭州为例，其它Region请按实际情况填写。
    bucket = oss2.Bucket(auth, 'http://oss-cn-hangzhou.aliyuncs.com', 'deepdraw-test')

    try: 
        for source_obj in org_pic:
            file_name = 'wzs_test.'+ source_obj.split('.')[-1]
        #source_obj = str(user_id)+'/pic/'+uuid+'.png'
        # 下载OSS文件到本地文件。如果指定的本地文件存在会覆盖，不存在则新建。
            bucket.get_object_to_file(source_obj, file_name)
        #计算MD5
            md5 = image_md5(file_name)
        #生成新obj名字
            new_obj_name = str(user_id)+'/pic/' + md5[:2] + '/' + md5 + '.' + source_obj.split('.')[-1]
       # print(source_obj)
       # print(new_obj_name)
        #通过copy-delete重命名
            bucket.copy_object('deepdraw-test', source_obj, new_obj_name)
            bucket.delete_object(source_obj)
        ret = {'code':1001,
               'msg':'重命名成功',
              }
    except:
        ret = {'code':1000,
               'msg':'重命名失败',
              }
    return ret

def deepdraw_product_matting(input_url,pic_id,result_obj_name):#---------------------用于单张抠图---------
    import json
    import requests
   # inputparams = []
   # url_dic = {}
    #单个图片就发起一次请求
    inputparams = []
    url_dic = {}

    url_dic["pic_url"] = input_url
    inputparams.append(url_dic)

    input_dic = {
                    "action": "wclothes_matting",
                    "inputparams": inputparams,
                    "model": "default",
                    "proj": "unet",
                    "exec": "online"
                }
    input_json = json.dumps(input_dic)

    print(type(input_json))

    request_url = '''http://47.96.132.7:8083/polls/analyze_str/?str='''+input_json
    print(request_url)
    result = requests.get(request_url)
    
    data = json.loads(result.text)
    #new_url = 'http://47.96.132.7:81/output/'+data['date_str']+'/rbg/product_matting/'+data['task_uuid_list'][0]+'/'+data['predictions'][0]['postproc']
    new_url = 'http://47.96.132.7:81/output/'+data['date_str']+'/'+input_dic['proj']+'/'+input_dic['action']+'/'+data['task_uuid_list'][0]+'/'+data['predictions'][0]['postproc']
    #PicInfo.objects.filter(id=pic_id).update(result_pic_url=new_url)
    #转存自有oss
    import oss2
# 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
    auth = oss2.Auth('LTAI4VIH8rP2cjtg', 'uzXZC3TB4egoT5FZe0nYn1BsoqXo5x')
# Endpoint以杭州为例，其它Region请按实际情况填写。
    bucket = oss2.Bucket(auth, 'http://oss-cn-shanghai-internal.aliyuncs.com', 'deepdraw-zip')

# requests.get返回的是一个可迭代对象（Iterable），此时Python SDK会通过Chunked Encoding方式上传。
    input = requests.get(new_url)
    @retry()
    def copyoss(result_obj_name, input):
        bucket.put_object(result_obj_name, input)
    copyoss(result_obj_name, input)
    result_url = 'https://deepdraw-zip.oss-cn-shanghai.aliyuncs.com/' + result_obj_name
    PicInfo.objects.filter(id=pic_id).update(pic_status = 3,result_pic_url=result_url)
    return result_url

def deepdraw_product_matting_v1(input_url,result_obj_name):#---------------------用于单张抠图---------
    import json
    import requests
   # inputparams = []
   # url_dic = {}
    #单个图片就发起一次请求
    inputparams = []
    url_dic = {}

    url_dic["pic_url"] = input_url
    inputparams.append(url_dic)

    input_dic = {
                    "action": "wclothes_matting",
                    "inputparams": inputparams,
                    "model": "default",
                    "proj": "unet",
                    "exec": "online"
                }
    input_json = json.dumps(input_dic)

    print(type(input_json))

    request_url = '''http://47.96.132.7:8083/polls/analyze_str/?str='''+input_json
    result = requests.get(request_url)

    data = json.loads(result.text)
    #new_url = 'http://47.96.132.7:81/output/'+data['date_str']+'/rbg/product_matting/'+data['task_uuid_list'][0]+'/'+data['predictions'][0]['postproc']
    new_url = 'http://47.96.132.7:81/output/'+data['date_str']+'/'+input_dic['proj']+'/'+input_dic['action']+'/'+data['task_uuid_list'][0]+'/'+data['predictions'][0]['postproc']
    #PicInfo.objects.filter(id=pic_id).update(result_pic_url=new_url)
    #转存自有oss
    import oss2
# 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
    auth = oss2.Auth('LTAI4VIH8rP2cjtg', 'uzXZC3TB4egoT5FZe0nYn1BsoqXo5x')
# Endpoint以杭州为例，其它Region请按实际情况填写。
    bucket = oss2.Bucket(auth, 'http://oss-cn-hangzhou.aliyuncs.com', 'deepdraw-test')

# requests.get返回的是一个可迭代对象（Iterable），此时Python SDK会通过Chunked Encoding方式上传。
    input = requests.get(new_url)
    @retry()
    def copyoss(result_obj_name, input):
        bucket.put_object(result_obj_name, input)
    copyoss(result_obj_name, input)
    result_url = 'https://deepdraw-test.oss-cn-hangzhou.aliyuncs.com/' + result_obj_name
    PicInfo.objects.filter(id=pic_id).update(pic_status = 3,result_pic_url=result_url)
    return result_url

def deepdraw_batch(input_url_list,pic_id_list):   #--------------------用于批量抠图---------
    import json
    import requests
    inputparams = []
    new_url_list = []
    url_dic = {}
    for input_url in input_url_list:
        url_dic["pic_url"] = input_url
        inputparams.append(url_dic)

    input_dic = {
                    "action": "wclothes_matting",
                    "inputparams": inputparams,
                    "model": "default",
                    "proj": "unet",
                    "exec": "online"
                }
    input_json = json.dumps(input_dic)

    print(type(input_json))

    request_url = '''http://47.96.132.7:8083/polls/analyze_str/?str='''+input_json
    
    result = requests.get(request_url)
    data = json.loads(result.text)
    for i in range(len(data['predictions'])):
        new_url = 'http://47.96.132.7:81/output/'+data['date_str']+'/'+input_dic['proj']+'/'+input_dic['action']+'/'+data['task_uuid_list'][i]+'/'+data['predictions'][i]['postproc']
        new_url_list.append(new_url)
    for pic_id,new_url in zip(pic_id_list,new_url_list):
        PicInfo.objects.filter(id=pic_id).update(result_pic_url=new_url)
    return new_url_list


def get_tocken():
    import uuid
    return str(uuid.uuid1())

def creat_pic(org_pic, org_pic_name,user_id,error_pic_name,task_id):
    pic_id_list = []


    for i in range(len(org_pic)):
        obj = PicInfo.objects.create(pic_status=1,
                                     pic_name=org_pic_name[i],
                                     pic_uuid=org_pic[i],
                                     task_id= task_id,
                                     user_id=user_id,
                                     org_pic_url = 'https://deepdraw-test.oss-cn-hangzhou.aliyuncs.com/'+org_pic[i],
                                     result_pic_url = ''
                                     )
        pic_id_list.append(obj.id)
    return pic_id_list

def creat_pic_v2(org_pic, org_pic_name,user_id,error_pic_name,task_id,bg,size,org_size):
    pic_id_list = []
    
   
    for i in range(len(org_pic)):
        obj = PicInfo.objects.create(pic_status=1,
                                     pic_name=org_pic_name[i],
                                     pic_uuid=org_pic[i],
                                     task_id= task_id,
                                     user_id=user_id,
                                     org_pic_url = 'https://deepdraw-test.oss-cn-hangzhou.aliyuncs.com/'+org_pic[i],
                                     result_pic_url = '',
                                     pic_bg = bg,
                                     pic_size = size,
                                     pic_org_size = org_size[i],
                                     )
        pic_id_list.append(obj.id)
#    for i in range(len(error_pic_name)):
 #       obj = PicInfo.objects.create(pic_status=2,
  #                                   pic_name=error_pic_name[i],
   #                                  pic_uuid=org_pic[i],
    #                                 task_id=task_id,
     #                                user_id=user_id,
      #                               org_pic_url = '',
       #                              result_pic_url = ''
                                    # result_url = ''
       #                              )
#        pic_id_list.append(obj.id)

    return pic_id_list


def get_random_code(len):##获取指定长度的随机验证码
    import random

    code_list = []
    for i in range(10):  # 0-9数字
        code_list.append(str(i))
    myslice = random.sample(code_list, len)  # 从list中随机获取6个元素，作为一个片断返回
    verification_code = ''.join(myslice)  # list to string
    return verification_code

##################-------------------------------------------------------------------------------

##################视图接口CBV---------------------------------------------------------------------
    '''
    用于用户任务查询和提交
    '''
class GetTaskView(APIView):
    #authentication_classes = [Authentication,]

    def post(self, request, *args, **kwargs):
        data = request.data
        token = data['token']
        user_id = data['user_id']
        now_page = int(data['now_page'])-1
        page_size = int(data['page_size'])
        type = data['type']
        result = []
        test_obj = UserToken.objects.filter(user_id=user_id, token=token)
        if not test_obj:
            ret = {'code': 1000,
                   'msg': '认证失败',
                   }
        else:
            try:
                if type == '1':
                    obj = TaskInfo.objects.filter(id=data['task_id'])

                elif type == '2':
                    obj = TaskInfo.objects.filter(user_id=data['user_id'])[now_page:now_page+page_size]

                for item in obj:
                    result.append(model_to_dict(item))

                ret = {'code':1001,
                       'msg':'获取成功',
                       'result': result,
                       }
            except Exception as e:
                ret = {'code': 1002,
                       'msg': '获取失败',
                       }
        return JsonResponse(ret)

class GetHistoryPicView(APIView):
    #authentication_classes = [Authentication,]

    def post(self, request, *args, **kwargs):
        data = request.data
        token = data['token']
        user_id = data['user_id']
        now_page = int(data['now_page'])-1
        page_size = int(data['page_size'])
        type = data['type']
        result = []
        test_obj = UserToken.objects.filter(user_id=user_id, token=token)
        if not test_obj:
            ret = {'code': 1000,
                   'msg': '认证失败',
                   }
        else:
            try:
                if type == '1':
                    obj = PicInfo.objects.filter(user_id=data['user_id'])[now_page:now_page+page_size]

               # for item in obj:
                #    result.append(model_to_dict(item))

                elif type == '2':
                    obj = TaskInfo.objects.filter(user_id=data['user_id'])[now_page:now_page+page_size]

                for item in obj:
                    result.append(model_to_dict(item))

                ret = {'code':1001,
                       'msg':'获取成功',
                       'result': result,
                       }
            except Exception as e:
                ret = {'code': 1002,
                       'msg': '获取失败',
                       }
        return JsonResponse(ret)

class TaskView(APIView):

    def post(self, request, *args, **kwargs):
        
        data = request.data
        token = data['token']
        user_id = str(data['user_id'])
        org_pic = data['org_pic'].split(',')
        org_pic_name = data['org_pic_name']#.split(',')
        error_pic_name = data['org_pic_name']#.split(',')
        
        print('--org_pic:'+str(org_pic)) 
        '''
        if len(org_pic) != len(org_pic_name):
            ret = {'code': 1003,
                   'msg': '图片统计错误',
                   }
            return JsonResponse(ret)
        '''
        test_obj = UserToken.objects.filter(user_id=user_id,token=token)
        if not test_obj:
            ret = {'code': 1000,
                   'msg': '认证失败',
                   }
            return JsonResponse(ret)
        else:
            print('permision_ok') 
           # source_obj = org_pic[0]
           # print(source_obj)
           # print(type(org_pic))
            try:
                obj = TaskInfo.objects.create(user_id=str(data['user_id']),
                                              task_status=data['task_status'],
                                              org_pic=str(data['org_pic']),
                                              org_pic_name=str(data['org_pic_name']),
                                              error_pic_name=str(data['error_pic_name'])
                                              )
                ctime= time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                #oss_rename(user_id, org_pic)
                import oss2
                #ret = oss_rename(user_id, org_pic)
                auth = oss2.Auth('LTAIDGyxdSloVIAu', 'WVOPeB83DdojWcfs3wF6X6Ry0XNZYU')
                # Endpoint以杭州为例，其它Region请按实际情况填写。
                bucket = oss2.Bucket(auth, 'http://oss-cn-hangzhou.aliyuncs.com', 'deepdraw-test')
                pic_id_list = creat_pic(org_pic, org_pic_name, user_id, error_pic_name, obj.id)
                #for source_obj in org_obj: 
                url_list = []
                result_url_list = []
                for source_obj,pic_id in zip(org_pic,pic_id_list):
                    print('pic_id:'+str(pic_id))
                                        
                    try_count = 0
                    #@retry()
                    def rename(source_obj,try_count):
                        try_count = try_count + 1
                        print('第{}次重试oss命名。'.format(try_count))
                        file_name = 'wzs_test.'+ source_obj.split('.')[-1]
                        #source_obj = str(user_id)+'/pic/'+uuid+'.png'
                        # 下载OSS文件到本地文件。如果指定的本地文件存在会覆盖，不存在则新建。
                        bucket.get_object_to_file(source_obj, file_name)
                        #计算MD5
                        md5 = image_md5(file_name)
                        #生成新obj名字
                        new_obj_name = 'input_folder/'+ str(user_id)+'/pic/' + md5[:2] + '/' + md5 + '.' + source_obj.split('.')[-1]
                        result_obj_name = 'input_folder/'+ str(user_id)+'/pic/' + md5[:2] + '/result_' + md5 + '.' + source_obj.split('.')[-1]
                        # print(source_obj)
                        # print(new_obj_name)
                      
                         #通过copy-delete重命名
                   
                        bucket.copy_object('deepdraw-test', source_obj, new_obj_name)
                        bucket.delete_object(source_obj)
                        print('-----------source_obj:' + source_obj)
                        url = 'https://deepdraw-test.oss-cn-hangzhou.aliyuncs.com/' + new_obj_name
                        url_list.append(url)
                        
                        print('-----------rename-oss-url:'+url)
                        return url,result_obj_name
                    
                    #url,result_obj_name = rename(source_obj,try_count)  #md5后端重命名：input_folder/user_id/pic/md5[:2]/md5.png
                    url = 'https://deepdraw-test.oss-cn-hangzhou.aliyuncs.com/'+source_obj  #不重命名:user_id/pic/task_uuid/0.png
                    result_obj_name ='result/' + source_obj  #不重命名
                    url_list.append(url) 
                    if len(org_pic) == 1:
                        result_url = deepdraw_product_matting(url,pic_id,result_obj_name)   #调用抠图接口
                        print('CALLING API')
                        result_url_list.append(result_url)
                    else:
                        result_url = deepdraw_product_matting(url,pic_id,result_obj_name)
                        print('CALLING API')
                        result_url_list.append(result_url)                   
                        pass
              #  if len(org_pic) != 1:
                  #  result_url = deepdraw_product_matting(url,pic_id)   #调用抠图接口
                   # print('CALLING API')
                   # result_url_list.append(result_url)
                    #result_url_list= deepdraw_batch(url_list,pic_id_list) 

                #rmbg_pic_url_list = ess_sdk(user_id,url_list,org_pic)  #remove.bg接口，要配置ssl证书
                #deepdraw_pic_url_list = deepdraw_product_matting()
                ret = {'code': 1001,
                       'msg': '抠图成功',
                       'ctime':ctime,
                       'task_id':obj.id,
                       'pic_id_list':pic_id_list,
                       'url_list':url_list,
                       'result_url_list':result_url_list,#'result_pic':rmbg_pic_url_list,
                       #'result_pic':deepdraw_pic_url_list,
                       }


            except :#Exception as e:
                ret = {'code': 1002,
                       'msg': '抠图失败',
                       'org_pic':org_pic,
                       #'url_list':url_list,
                       #'source_obj':source_obj,
                       #'new_obj_name':new_obj_name,
                       }

        return JsonResponse(ret)

class PutTaskView(APIView):

    def post(self, request, *args, **kwargs):

        data = request.data
        token = data['token']
        user_id = data['user_id']
        org_pic = data['org_pic']#.split(',')
        org_pic_name = data['org_pic_name']#.split(',')
        error_pic_name = data['org_pic_name']#.split(',')
        bg = data['bg']
        size = data['size']
        org_size = data['org_size']
        print('--org_pic:'+str(org_pic))
        
        test_obj = UserToken.objects.filter(user_id=user_id,token=token)
        if not test_obj:
            ret = {'code': 1000,
                   'msg': '认证失败',
                   }
            return JsonResponse(ret)
        else:
            print('permision_ok')
            try:
                obj = TaskInfo.objects.create(user_id=data['user_id'],
                                              task_status=data['task_status'],
                                              org_pic=data['org_pic'],
                                              org_pic_name=data['org_pic_name'],
                                              error_pic_name=data['error_pic_name'],
                                              bg = bg,
                                              size = size,
                                              org_size = org_size,
                                              )
                url_list = []
                for source_obj in org_pic:
                    url = 'https://deepdraw-test.oss-cn-hangzhou.aliyuncs.com/'+source_obj
                    url_list.append(url)
                ctime= time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                #oss_rename(user_id, org_pic)
                import oss2
                #ret = oss_rename(user_id, org_pic)
                auth = oss2.Auth('LTAIDGyxdSloVIAu', 'WVOPeB83DdojWcfs3wF6X6Ry0XNZYU')
                # Endpoint以杭州为例，其它Region请按实际情况填写。
                bucket = oss2.Bucket(auth, 'http://oss-cn-hangzhou.aliyuncs.com', 'deepdraw-test')
                pic_id_list = creat_pic_v2(org_pic, org_pic_name, user_id, error_pic_name, obj.id, bg, size, org_size)
                ret = {'code': 1001,
                       'msg':'任务提交成功',
                       'task_id':obj.id,
                       'pic_id_list':pic_id_list,
                       'url_list':url_list,
                      }
            except:
                ret = {'code':1000,
                       'msg':'任务提交失败',
                      }
        return JsonResponse(ret)

class StartTaskView(APIView):

    def post(self, request, *args, **kwargs):

        data = request.data
        print(data)
        token = data['token']
        print('token'+str(token))
        user_id = str(data['user_id'])
        org_pic = data['org_pic']#.split(',')
        pic_id_list = data['pic_id_list']#.split(',')        
        size = data['size']
        print('--org_pic:'+str(org_pic))
        print(type(org_pic)) 
        test_obj = UserToken.objects.filter(user_id=user_id,token=token)
        if not test_obj:
            ret = {'code': 1000,
                   'msg': '认证失败',
                   }
            return JsonResponse(ret)
        else:
            print('permision_ok')
           # source_obj = org_pic[0]
           # print(source_obj)
           # print(type(org_pic))
            try:
                ctime= time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                #oss_rename(user_id, org_pic)
                import oss2
                #ret = oss_rename(user_id, org_pic)
                auth = oss2.Auth('LTAIDGyxdSloVIAu', 'WVOPeB83DdojWcfs3wF6X6Ry0XNZYU')
                #Endpoint以杭州为例，其它Region请按实际情况填写。
                bucket = oss2.Bucket(auth, 'http://oss-cn-hangzhou.aliyuncs.com', 'deepdraw-test')
                url_list = []
                result_url_list = []
                for source_obj,pic_id in zip(org_pic,pic_id_list):
                   
                    try_count = 0
                    #@retry()
                    def rename(source_obj,try_count):
                        try_count = try_count + 1
                        print('第{}次重试oss命名。'.format(try_count))
                        file_name = 'wzs_test.'+ source_obj.split('.')[-1]
                        #source_obj = str(user_id)+'/pic/'+uuid+'.png'
                        # 下载OSS文件到本地文件。如果指定的本地文件存在会覆盖，不存在则新建。
                        bucket.get_object_to_file(source_obj, file_name)
                        #计算MD5
                        md5 = image_md5(file_name)
                        #生成新obj名字
                        new_obj_name = 'input_folder/'+ str(user_id)+'/pic/' + md5[:2] + '/' + md5 + '.' + source_obj.split('.')[-1]
                        result_obj_name = 'input_folder/'+ str(user_id)+'/pic/' + md5[:2] + '/result_' + md5 + '.' + source_obj.split('.')[-1]
                        bucket.copy_object('deepdraw-test', source_obj, new_obj_name)
                        bucket.delete_object(source_obj)
                        print('-----------source_obj:' + source_obj)
                        url = 'https://deepdraw-test.oss-cn-hangzhou.aliyuncs.com/' + new_obj_name
                        url_list.append(url)

                        print('-----------rename-oss-url:'+url)
                        return url,result_obj_name

                    #url,result_obj_name = rename(source_obj,try_count)  #md5后端重命名：input_folder/user_id/pic/md5[:2]/md5.png
                    if size == "800":
                        url = 'https://deepdraw-test.oss-cn-hangzhou-internal.aliyuncs.com/'+source_obj+'!resize_800'  #不重命名:user_id/pic/task_uuid/0.png
                    elif size == "1200":
                        url = 'https://deepdraw-test.oss-cn-hangzhou-internal.aliyuncs.com/'+source_obj+'!resize_1200'
                    else:
                        url = 'https://deepdraw-test.oss-cn-hangzhou-internal.aliyuncs.com/'+source_obj
                    result_obj_name ='result/' + source_obj  #不重命名
                    url_list.append(url)
                    print(url_list)
                    if len(org_pic) == 1:
                        print('CALLING API')
                        result_url = deepdraw_product_matting(url,pic_id,result_obj_name)   #调用抠图接口
             
                        result_url_list.append(result_url)
                    else:
                        print('CALLING API')
                        result_url = deepdraw_product_matting(url,pic_id,result_obj_name)
                        result_url_list.append(result_url)
                       
                            
                ret = {'code': 1001,
                       'msg': '抠图成功',
                    #   'task_id':obj.id,
                       #'url_list':url_list,
                      # 'result_url_list':result_url_list,#'result_pic':rmbg_pic_url_list,
                       #'result_pic':deepdraw_pic_url_list,
                       }


            except :#Exception as e:
                ret = {'code': 1002,
                       'msg': '抠图失败',
                       'org_pic':org_pic,
                       #'url_list':url_list,
                       #'source_obj':source_obj,
                       #'new_obj_name':new_obj_name,
                       }

        return JsonResponse(ret)

class Download(APIView):
    def post(self, request, *args, **kwargs):
        auth = oss2.Auth('LTAI4VIH8rP2cjtg', 'uzXZC3TB4egoT5FZe0nYn1BsoqXo5x')
        #Endpoint为上海，因为本服务器在上海走内网。
        bucket = oss2.Bucket(auth, 'http://oss-cn-shanghai-internal.aliyuncs.com', 'deepdraw-zip')
        data = request.data
        pic_id_list = data['pic_id_list']
        token = data['token']
        user_id = str(data['user_id'])
        test_obj = UserToken.objects.filter(user_id=user_id,token=token)
        if not test_obj:
            ret = {'code': 1000,
                   'msg': '认证失败',
                   }
            return JsonResponse(ret)
        else:
            ctime = time.strftime("%Y%m%d-%H:%M:%S", time.localtime())
            zip_filename = '/root/deepdraw/untitled/zip/'+ctime+'.zip'
            f = zipfile.ZipFile(zip_filename, 'w' ,zipfile.ZIP_DEFLATED) 
            for id in pic_id_list:
                obj = PicInfo.objects.filter(id=id).first()
                obj_name = 'result/' + obj.pic_uuid
                download_name = obj_name.split('/')[-2] + '-' + obj_name.split('/')[-1]
                bucket.get_object_to_file(obj_name, '/root/deepdraw/untitled/makezip/' + download_name)
                f.write('makezip/' + download_name)
            f.close()
            zip_objname = 'zip/'+user_id+'/'+ctime+'.zip'
            
            bucket.put_object_from_file(zip_objname,zip_filename)
            zip_url = 'https://deepdraw-zip.oss-cn-shanghai.aliyuncs.com/'+zip_objname
            ret = {'code':1001,
                   'msg':'压缩成功',
                   'zip_url':zip_url,
                   }
                
        return JsonResponse(ret)

class PicView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        token = data['token']
        user_id = data['user_id']
       
        test_obj = UserToken.objects.filter(user_id=user_id, token=token)
        if not test_obj:
            ret = {'code': 1000,
                   'msg': '认证失败',
                   }
            return JsonResponse(ret)
        else:
            try:
                obj = PicInfo.objects.filter(task_id=data['task_id'])
                result = []
                for item in obj:
                    result.append(model_to_dict(item))
                ret = {'code': 1001,
                       'msg': '获取成功',
                       'result': result,
                       }
            except:
                ret = {'code':1000,
                       'msg':'获取失败'
                       }
            return JsonResponse(ret)

class GetPicView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        token = data['token']
        user_id = data['user_id']
        pic_id = data['pic_id']
        test_obj = UserToken.objects.filter(user_id=user_id, token=token)
        if not test_obj:
            ret = {'code': 1000,
                   'msg': '认证失败',
                   }
            return JsonResponse(ret)
        else:
            try:
               obj = PicInfo.objects.filter(id=pic_id)
               result = []
               for item in obj:
                   result.append(model_to_dict(item))
               ret = {'code': 1001,
                      'msg': '获取成功',
                      'result': result,
                      'url_list': [result[0]['result_pic_url']],
                      }
            except:
                ret = {'code':1000,
                       'msg':'获取失败'
                       }
            return JsonResponse(ret)

class Oss(APIView):
    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        ret = oss_sdk()
        return JsonResponse(ret)



class OssKeyView(APIView):
    def post(self, request, *args, **kwargs):
        AccessId = 'LTAI4VIH8rP2cjtg'
        AccessSecret = 'uzXZC3TB4egoT5FZe0nYn1BsoqXo5x'
        data = request.data
        token = data['token']
        user_id = data['user_id']
        test_obj = UserToken.objects.filter(user_id=user_id,token=token)
        if not test_obj:
            ret = {'code': 1000,
                   'msg': '认证失败',
                   }
        else:
            try:
                ret = {'code': 1001,
                       'msg': '获取AccessKey成功',
                       'AccessId':AccessId,
                       'AccessSecret':AccessSecret,
                       }

            except Exception as e:
                ret = {'code': 1002,
                       'msg': '获取失败',
                       }

        return JsonResponse(ret)


class TouristView(APIView):
    def post(self, request, *args, **kwargs):
        ret = {'id':2,
               'token' : '71dcb9c2-a225-11e9-9e3f-00e070884750'
              }
        return JsonResponse(ret)






