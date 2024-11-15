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

    def delete(self, *args, **kwargs):
        """
        Availability 삭제 시 Slot 업데이트 및 필요하면 삭제
        """
        current_time = self.time_from
        while current_time < self.time_to:
            try:
                # 관련 Slot 찾기
                slot = Slot.objects.get(days=self.days, time=current_time)
                # availability_count 감소
                if slot.availability_count > 0:
                    slot.availability_count -= 1
                    slot.save()

                # availability_count가 0이면 Slot 삭제
                if slot.availability_count == 0:
                    slot.delete()
            except Slot.DoesNotExist:
                pass

            # 시간 증가 (30분 단위)
            current_time = (datetime.datetime.combine(datetime.date.today(), current_time) +
                            datetime.timedelta(minutes=30)).time()

        # Availability 삭제
        super().delete(*args, **kwargs)

    
class Slot(models.Model):
    id = models.AutoField(primary_key=True)
    days = models.ForeignKey(Days, related_name="slots", on_delete=models.CASCADE)
    availability_count = models.PositiveIntegerField(null=False, default=0, verbose_name='가능 인원 수')
    time = models.TimeField(null=False, default=datetime.time(0, 0, 0), verbose_name='슬롯 시간')

    def __str__(self):
        return f'{self.days.group.name}의 슬롯 : {self.time} (인원: {self.availability_count})'
    
    class Meta:
        unique_together = ('days', 'time')

