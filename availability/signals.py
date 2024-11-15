from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Availability, Slot
import datetime

@receiver(post_delete, sender=Availability)
def update_or_delete_slot_after_availability_delete(sender, instance, **kwargs):
    """
    Availability 삭제 시 관련 Slot 업데이트 및 필요하면 삭제
    """
    current_time = instance.time_from
    while current_time < instance.time_to:
        try:
            # 관련 Slot 찾기
            slot = Slot.objects.get(days=instance.days, time=current_time)
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
