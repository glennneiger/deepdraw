from django.db import models


# Create your models here.
class Tripletmark(models.Model):
    uuid1 = models.CharField(max_length=100)
    uuid2 = models.CharField(max_length=100)
    bbox1 = models.CharField(max_length=100)
    bbox2 = models.CharField(max_length=100)
    mark = models.CharField(max_length=10)
    fix = models.CharField(max_length=10)
    unique_together = (('uuid', 'uuid2', 'bbox1', 'bbox2'),)
