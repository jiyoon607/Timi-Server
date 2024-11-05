import datetime
from django.db import models

# Create your models here.
class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False, verbose_name='그룹 이름')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Days(models.Model):
    DAY_CHOICES = [
        ('Mon', '월'),
        ('Tue', '화'),
        ('Wed', '수'),
        ('Thu', '목'),
        ('Fri', '금'),
        ('Sat', '토'),
        ('Sun', '일'),
    ]

    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAY_CHOICES, verbose_name='요일')
    date = models.DateField(null=True, verbose_name='날짜')
    start_time = models.TimeField(null=False, default=datetime.time(9, 0, 0), verbose_name='시작 시간')
    end_time = models.TimeField(null=False, default=datetime.time(22, 0, 0), verbose_name='종료 시간')

