from django.db import models


# Create your models here.
class CheckPics(models.Model):
    uuid = models.CharField(max_length=500)
    bbox = models.CharField(max_length=200)  # bbox
    mark = models.CharField(max_length=10)  # 输入结果
    fix = models.CharField(max_length=10)  # 打标结果
    status = models.CharField(max_length=10)  # 是否打标
    choice = models.CharField(max_length=10)  # 是否需要
