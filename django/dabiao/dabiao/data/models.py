from django.db import models


# Create your models here.
class Tripletmark(models.Model):
    uuid1 = models.CharField(max_length=500)
    uuid2 = models.CharField(max_length=500)
    bbox1 = models.CharField(max_length=100)
    bbox2 = models.CharField(max_length=100)
    mark = models.CharField(max_length=10)
    fix = models.CharField(max_length=10)
    status = models.CharField(max_length=10, default='0', db_index=True)
    types = models.CharField(max_length=30)
    unique_together = (('uuid1', 'uuid2', 'bbox1', 'bbox2'),)
