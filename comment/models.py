import datetime
from django.db import models
from group.models import *
# Create your models here.
class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    days = models.ForeignKey(Days, on_delete=models.CASCADE)
    time = models.TimeField(null=False)
    text = models.TextField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)