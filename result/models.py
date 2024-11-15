import datetime
from django.db import models
from group.models import *
# Create your models here.
class Result(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    place = models.CharField(max_length=200, null=True)
    time = models.CharField(max_length=200, null=True)