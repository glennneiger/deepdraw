from django.db import models

# Create your models here.
class UserInfo(models.Model):
    user_type_choices = (
        (1,'普通用户'),
        (2,'vip'),
        (3,'svip'),
        (4,'amdin'),
    )
    #user_id = models.IntegerField(unique=True)
    user_type = models.IntegerField(choices=user_type_choices)
    user_name = models.CharField(max_length=10,unique=True)
    password = models.CharField(max_length=20)
    user_detil = models.CharField(max_length=60)

    def __str__(self):
        return self.user_name

class UserToken(models.Model):
    user = models.OneToOneField(UserInfo, on_delete=models.CASCADE)
    token = models.CharField(max_length=64)

class TaskInfo(models.Model):
    task_status_choices = (
        (1, '提交成功'),
        (2, '提交失败'),
        (3, '任务完成但有问题'),
        (4, '任务完成'),
    )
    task_status = models.IntegerField(choices=task_status_choices)
    task_ctime = models.DateTimeField(auto_now_add=True)
    org_pic_name = models.CharField(max_length=6400000)
    error_pic_name = models.CharField(max_length=3200000)
    org_pic = models.CharField(max_length=3200000)
    result_pic = models.CharField(max_length=3200000)
    bg = models.CharField(max_length=3200000)
    size = models.CharField(max_length=3200000)
    org_size = models.CharField(max_length=3200000)
    
    user = models.ForeignKey(
        'UserInfo',
        on_delete=models.CASCADE,
    )

class PicInfo(models.Model):
    pic_status_choices = (
        (1, '上传成功'),
        (2, '上传失败'),
        (3, '抠图成功'),
        (4, '抠图失败'),
        (5, '图片重复'),
    )
    pic_status = models.IntegerField(choices=pic_status_choices)
    pic_name = models.CharField(max_length=64)
    pic_uuid = models.CharField(max_length=64)
    pic_ctime = models.DateTimeField(auto_now_add=True)
    pic_size = models.CharField(max_length=64)
    pic_org_size = models.CharField(max_length=64)
    pic_bg = models.CharField(max_length=64) 
    org_pic_url = models.CharField(max_length=200)
    result_pic_url = models.CharField(max_length=200)
    user = models.ForeignKey(
        'UserInfo',
        on_delete=models.CASCADE,
    )
    task = models.ForeignKey(
        'TaskInfo',
        on_delete=models.CASCADE,
    )
