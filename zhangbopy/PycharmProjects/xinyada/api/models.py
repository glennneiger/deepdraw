from django.db import models


# Create your models here.
class PicInfo(models.Model):
    user_type_choices = (
        (1, '身份证'),
        (2, '驾照'),
        (3, '银行卡'),
        (4, '其他'),
    )
    # user_id = models.IntegerField(unique=True)
    pic_type = models.IntegerField(choices=user_type_choices)
    pic_name = models.CharField(max_length=30, unique=False)
    pic_path = models.CharField(max_length=50,unique=False)
     # = models.CharField(max_length=60)