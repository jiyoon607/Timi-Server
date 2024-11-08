import datetime
from django.db import models
from group.models import *
# Create your models here.

class Availability(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    days = models.ForeignKey(Days, on_delete=models.CASCADE)
    time_from = models.TimeField(null=False, default=datetime.time(0, 0, 0), verbose_name='가능 시작 시간')
    time_to = models.TimeField(null=False, default=datetime.time(0, 0, 0), verbose_name='가능 종료 시간')

    def __str__(self):
        return f'{self.user.name}의 가능 시간 : {self.time_from} ~ {self.time_to}'
    
class Slot(models.Model):
    id = models.AutoField(primary_key=True)
    days = models.ForeignKey(Days, related_name="slots", on_delete=models.CASCADE)
    availability_count = models.PositiveIntegerField(null=False, default=0, verbose_name='가능 인원 수')
    time = models.TimeField(null=False, default=datetime.time(0, 0, 0), verbose_name='슬롯 시간')

    def __str__(self):
        return f'{self.days.group.name}의 슬롯 : {self.time} (인원: {self.availability_count})'
    
    class Meta:
        unique_together = ('days', 'time')

