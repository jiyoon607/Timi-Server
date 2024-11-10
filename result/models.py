import datetime
from django.db import models
from group.models import *
# Create your models here.
class Result(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    text = models.TextField(max_length=200)