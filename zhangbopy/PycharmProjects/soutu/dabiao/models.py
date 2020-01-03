from django.db import models

# Create your models here.
class Mark_Pic(models.Model):
    pic_mark_choices = (
        (0,'未处理'),
        (1,'相似'),
        (2,'不相似'),
        (3,'无法判断'),
    )
    url = models.CharField(max_length=200)
    class_id = models.IntegerField(max_length=11)
    t = models.FloatField(max_length=40)
    r = models.FloatField(max_length=40)
    b = models.FloatField(max_length=40)
    l = models.FloatField(max_length=40)
    value = models.FloatField(max_length=50)
    isMain = models.IntegerField(max_length=11)
    status = models.IntegerField(choices=pic_mark_choices)
    unique_together = (('url', 'class_id'),)
    def __str__(self):
        return self.url

class Get_Task(models.Model):
    task_status_choices = (
        (0, '未分配'),
        (1, '分配未完成'),
        (2, '已提交'),



















    )
    class_id = models.IntegerField(max_length=11)
    status = models.IntegerField(max_length=10)
    user = models.CharField(max_length=70,default="NULL")

class User_Info(models.Model):
 #   User_status_choices = (
 #       (0, ''),
 #       (1, '分配未完成'),
 #       (2, '已提交'),
 #   )
    user_type_choices = (
        (1,'普通用户'),
        (2,'vip'),
        (3,'svip'),
        (4,'amdin'),
    )
    user_type = models.IntegerField(choices=user_type_choices)
    user_name = models.CharField(max_length=10,unique=True)
    password = models.CharField(max_length=20)
    user_detil = models.CharField(max_length=60)

    def __str__(self):
        return self.user_name
