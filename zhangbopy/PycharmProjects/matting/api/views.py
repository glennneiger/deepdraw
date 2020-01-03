from django.utils.decorators import method_decorator
import json,time,os,requests,json
from random import randrange
from django.http import HttpResponse,JsonResponse
from rest_framework.views import APIView
from django.forms.models import model_to_dict
from api.models import UserInfo,UserToken,TaskInfo,PicInfo
from retry import retry
import oss2,zipfile
import threading
flag = 0 #捕获线程异常标志
#############全局配置参数-----------------------------------------------------------------------
model_url = "http://112.124.227.50:8088/hznz_framework/polls/analyze_str/?str=" #模型接口
model_output = "http://47.96.132.7:81/output/"#模型输出
pic_folder = os.getcwd()+"/pic/"              #用于存放图片,白色背景图片处理
zip_folder = os.getcwd()+"/zip/"              #用于存放打包的zip文件

oss_shanghai_internal = "https://deepdraw-zip.oss-cn-shanghai-internal.aliyuncs.com/"#本机oss内网
oss_shanghai = "https://deepdraw-zip.oss-cn-shanghai.aliyuncs.com/"                  #本机oss外网
oss_hangzhou_internal = "https://deepdraw-test.oss-cn-hangzhou-internal.aliyuncs.com/"#模型oss内网
oss_hangzhou = "https://deepdraw-test.oss-cn-hangzhou.aliyuncs.com/"                  #模型oss外网

AccessId = 'LTAI4VIH8rP2cjtg'
AccessSecret = 'uzXZC3TB4egoT5FZe0nYn1BsoqXo5x'
auth = oss2.Auth(AccessId, AccessSecret)                #oss秘钥
bucket = oss2.Bucket(auth, 'http://oss-cn-shanghai-internal.aliyuncs.com', 'deepdraw-zip')#bucket配置
###########-------------------------------------------------------------------------------------
###########短信验证码----------------------------------------------------------------------------
class MsgView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        Phone = data['Phone']
        code = get_random_code(len = 6)
        body = {"code":code}
        aliyun_msg = ''
        from aliyunsdkcore.client import AcsClient
        from aliyunsdkcore.request import CommonRequest
        client = AcsClient('LTAINoeFiTtb5Ldh', 'FxOZ9pfmLB9LwIBABsauu8Md8dJjn7', 'cn-hangzhou')#短信子账户
        try:
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
            request.add_query_param('TemplateParam', str(body))
     
            response = client.do_action(request)
            aliyun_msg = str(response, encoding='utf-8')
        
            test_obj = UserInfo.objects.filter(user_name=data['Phone']).first()
            if not test_obj:
                obj = UserInfo.objects.create(user_name=Phone,
                                              user_type=1,
                                              user_detil='手机注册',
                                              password=code,
                                              )

            else:
                UserInfo.objects.filter(user_name=Phone).update(user_name=Phone,password=code) 
                obj = UserInfo.objects.filter(user_name=Phone).first()

            ret = {'code':1001,
                   'msg':'获取验证码成功',
                   #'random_code':code, #调试时返回
                   'user_id':obj.id,
                   'aliyun_msg':aliyun_msg,
                   }
        except:
            ret = {'code':1000,
                   'msg':'获取验证码失败',
                   'aliyun_msg':aliyun_msg,
                   }
        return JsonResponse(ret)

###########------------------------------------------------------------------------------------

###########用户验证-----------------------------------------------------------------------------
class LoginView(APIView):

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
                token = get_token()
                #重置密码
                UserInfo.objects.filter(user_name=data['user_name'],
                                          password=data['password']).update(password=token[:10])
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
                   'msg': '请求异常'+str(e),
                   }
        return JsonResponse(ret)

################---------------------------------------------------------------------------------

################----------功能逻辑函数/装饰器-------------------------------------------------------------
def req_matting(input_url,pic_id,result_obj_name):#---------------------用于请求模型---------
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
    request_url = model_url+input_json
    try:
        result = requests.get(request_url,timeout = 6)
    except:
        global flag
        flag = 1
        print("flag:{}".format(flag))
        return 
    data = json.loads(result.text)
    new_url = model_output+data['date_str']+'/'+input_dic['proj']+'/'+input_dic['action']+'/'+data['task_uuid_list'][0]+'/'+data['predictions'][0]['out']
    return new_url,data['task_uuid_list'][0]

def matting_none(input_url,pic_id,result_obj_name):#----------------------用于透明抠图---------
    new_url,task_uuid = req_matting(input_url,pic_id,result_obj_name)
    #转存新oss避免接口暴露
    #requests.get返回的是一个可迭代对象（Iterable），此时Python SDK会通过Chunked Encoding方式上传。
    input = requests.get(new_url)
    @retry()
    def copyoss(result_obj_name, input):
        bucket.put_object(result_obj_name, input)
    copyoss(result_obj_name, input)

    result_url = oss_shanghai + result_obj_name
    PicInfo.objects.filter(id=pic_id).update(pic_status = 3,result_pic_url=result_url)

def matting_white(input_url,pic_id,result_obj_name):#---------------------用于白背抠图---------
    from PIL import Image
    new_url,task_uuid = req_matting(input_url,pic_id,result_obj_name)
    r = requests.get(new_url)
    white_pic_path = pic_folder + task_uuid+'.png'
    
    with open(white_pic_path,'wb') as f:
        f.write(r.content)
        f.close()

    def alphabg2white_PIL(img):##透明图转白色背景
        img=img.convert('RGBA')
        sp=img.size
        width=sp[0]
        height=sp[1]
    
        for yh in range(height):
            for xw in range(width):
                dot=(xw,yh)
                color_d=img.getpixel(dot)
                if(color_d[3]==0):
                    color_d=(255,255,255,255)
                    img.putpixel(dot,color_d)
        return img
    img = Image.open(white_pic_path)
    white1 = alphabg2white_PIL(img)
    white1.save(white_pic_path)
    
    bucket.put_object_from_file(result_obj_name, white_pic_path)

    result_url = oss_shanghai + result_obj_name
    PicInfo.objects.filter(id=pic_id).update(pic_status = 3,result_pic_url=result_url)

def get_token():##生成token,接入第三方登录可能有变,暂时uuid1
    import uuid
    return str(uuid.uuid1())

def creat_pic_v2(org_pic, org_pic_name,user_id,error_pic_name,task_id,bg,size,org_size):##任务转图片
    pic_id_list = []
    for i in range(len(org_pic)):
        obj = PicInfo.objects.create(pic_status=1,
                                     pic_name=org_pic_name[i],
                                     pic_uuid=org_pic[i],
                                     task_id= task_id,
                                     user_id=user_id,
                                     org_pic_url = oss_hangzhou + org_pic[i],
                                     result_pic_url = '',
                                     pic_bg = bg,
                                     pic_size = size,
                                     pic_org_size = org_size[i],
                                     )
        pic_id_list.append(obj.id)
    return pic_id_list

def get_random_code(len):##获取指定长度的随机验证码
    import random

    code_list = []
    for i in range(10):  # 0-9数字
        code_list.append(str(i))
    myslice = random.sample(code_list, len)  # 从list中随机获取6个元素，作为一个片断返回
    verification_code = ''.join(myslice)  # list to string
    return verification_code

def authencation(func):##token验证装饰器
    def author(request, *args, **kwargs):
        data = request.data
        token = data['token']
        user_id = data['user_id']
        test_obj = UserToken.objects.filter(user_id=user_id,token=token)
        if not test_obj:
            ret = {'code': 1000,
                   'msg': '认证失败',
                   }
            return JsonResponse(ret)
        return func(request, *args, **kwargs)
    return author#(self, request, *args, **kwargs)

##################-------------------------------------------------------------------------------

##################视图接口CBV---------------------------------------------------------------------
@method_decorator(authencation, name= 'post')
class PutTaskView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        user_id = data['user_id']
        org_pic = data['org_pic']
        org_pic_name = data['org_pic_name']
        error_pic_name = data['org_pic_name']
        bg = data['bg']
        size = data['size']
        org_size = data['org_size']
        
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
                url = oss_hangzhou + source_obj
                url_list.append(url)
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

@method_decorator(authencation, name= 'post')
class StartTaskView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        org_pic = data['org_pic']
        pic_id_list = data['pic_id_list']        
        size = data['size']
       
        try:
            url_list = []
            thread_list = []
            for source_obj,pic_id in zip(org_pic,pic_id_list):
                bg = PicInfo.objects.filter(id=pic_id).first().pic_bg
                #不查重不重命名:user_id/pic/task_uuid/0.png
                if size == "800":
                    url = oss_hangzhou_internal + source_obj + '!resize_800'  
                elif size == "1200":
                    url = oss_hangzhou_internal + source_obj + '!resize_1200'
                else:
                    url = oss_hangzhou_internal + source_obj
                uuid = get_token()
                result_obj_name ='result/' + source_obj[:-(len(source_obj.split('.')[-1])+1)] +'/'+ uuid +'.png'  #重命名
                url_list.append(url)
                if bg == 'none':
                    t = threading.Thread(target=matting_none,args=(url,pic_id,result_obj_name))
                    thread_list.append(t)
                else:
                    t = threading.Thread(target=matting_white,args=(url,pic_id,result_obj_name))
                    thread_list.append(t)
            for t in thread_list:
                t.start()
                t.join(5)
            global flag
            if flag == 1:
                 ret = {'code': 1000,
                        'msg': '抠图失败',
                        'org_pic':org_pic,
                       }
                 return JsonResponse(ret)

            ret = {'code': 1001,
                   'msg':"抠图成功"}

        except Exception as e:
            print(str(e))
            ret = {'code': 1000,
                   'msg': '抠图失败',
                   'org_pic':org_pic,
                   }

        return JsonResponse(ret)

@method_decorator(authencation, name= 'post')
class GetHistoryPicView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        user_id = data['user_id']
        now_page = int(data['now_page'])-1
        page_size = int(data['page_size'])
        type = data['type']
        result = []
        try:
            if type == '1':
                obj = PicInfo.objects.filter(user_id=data['user_id'])
                page_count = len(obj)//page_size
                count = len(obj)
                obj = obj[::-1][now_page*page_size:now_page*page_size+page_size]

            elif type == '2':
                obj = TaskInfo.objects.filter(user_id=data['user_id'])
                page_count = len(obj)//page_size
                count = len(obj)
                obj = obj[::-1][now_page*page_size:now_page*page_size+page_size]

            for item in obj:
                if type == '2':
                    result.append(model_to_dict(item))
                else:
                    dic = model_to_dict(item)
                    dic['task_code'] = str(dic['id'])+'/'+dic['pic_uuid'].split('/')[-2]
                    result.append(dic)

            if page_count%page_size!=0:
                page_count = page_count+1

            ret = {'code':1001,
                   'msg':'获取成功',
                   'count':count,
                   'result': result,
                   }
        except Exception as e:
            ret = {'code': 1000,
                   'msg': '获取失败',
                   }
        return JsonResponse(ret)

@method_decorator(authencation, name= 'post')
class Download(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        pic_id_list = data['pic_id_list']
        user_id = str(data['user_id'])

        ctime = time.strftime("%m%d-%H:%M:%S", time.localtime())
        zip_filename = zip_folder + ctime + '.zip'
        f = zipfile.ZipFile(zip_filename, 'w' ,zipfile.ZIP_DEFLATED) 
        for id in pic_id_list:
            obj = PicInfo.objects.filter(id=id).first()
            bg = "透明"
            size = obj.pic_org_size
            if obj.pic_bg == 'white':
                bg = "白背"
            if obj.pic_size == '800':
                size = "800*800"
            if obj.pic_size == '1200':
                size = "1200*1200"
            uuid = obj.pic_uuid
            pic_name = obj.pic_name
            obj_name = ''
            for item in obj.result_pic_url.split('/')[-6:]:
                obj_name = obj_name + '/' + item
            obj_name = obj_name[1:]
            download_name = '['+ pic_name +']'+'['+bg+']'+'['+size+']' +'['+ obj_name.split('/')[-2] +']'+ '_' + obj_name.split('/')[-1]
            bucket.get_object_to_file(obj_name, pic_folder + download_name)
            f.write('pic/' + download_name)
        f.close()
        zip_objname = 'zip/'+user_id+'/'+ctime+'.zip'
        bucket.put_object_from_file(zip_objname,zip_filename)
        zip_url = oss_shanghai + zip_objname
        ret = {'code':1001,
               'msg':'压缩成功',
               'zip_url':zip_url,
               }
                
        return JsonResponse(ret)

@method_decorator(authencation, name= 'post')
class PicView(APIView):##查询task_id下所有图片信息
    def post(self, request, *args, **kwargs):
        data = request.data
        user_id = data['user_id']
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

@method_decorator(authencation, name= 'post')
class GetPicView(APIView):##查询pic_id对应的图片
    def post(self, request, *args, **kwargs):
        data = request.data
        user_id = data['user_id']
        pic_id = data['pic_id']
        try:
           obj = PicInfo.objects.filter(id=pic_id)
           result = []
           for item in obj:
               result.append(model_to_dict(item))
           
           obj_1 = obj.first()

           uuid = obj_1.pic_uuid.split('/')[-2]
           task_code = pic_id+'/'+uuid
           ret = {'code': 1001,
                  'msg': '获取成功',
                  'result': result,
                  'task_code':task_code,
                  }
        except:
            ret = {'code':1000,
                   'msg':'获取失败'
                   }
        return JsonResponse(ret)

@method_decorator(authencation, name= 'post')
class OssKeyView(APIView):##获取osskey
    def post(self, request, *args, **kwargs):
        data = request.data
        user_id = data['user_id']
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


class TouristView(APIView):##获取游客token固定id=2便于管理
    def post(self, request, *args, **kwargs):
        ret = {'id':2,
               'token' : '9e3f8806-c26d-11e9-aae4-00163e068aa2'
              }
        return JsonResponse(ret)


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
                   'token': get_token()}

        except Exception as e:
            ret = {'code':1000,
                   'msg':'注册失败',
                   'e':str(e)
                   }

        return JsonResponse(ret)
