from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from datetime import datetime
from .models import *
from group.models import Group, Days
from .serializers import *
from group.serializers import DaysSerializer
from comment.models import Comment
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError


# Create your views here.
class GroupTimetableViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    serializer_class = DaysSerializer

    def get_queryset(self):
        return Days.objects.all()
    
    def get_object(self):
        group_id = self.kwargs.get('pk')
        object = get_object_or_404(Group, id=group_id)
        return object

    def retrieve(self, request, *args, **kwargs):
        group = self.get_object()
        days = Days.objects.filter(group=group)

        serialized_days = DaysSlotSerializer(days, many=True)

        return Response(serialized_days.data)


class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer

    def perform_create(self, serializer):
        user_pk = self.request.data.get('user')
        day = self.request.data.get('day')
        date = self.request.data.get('date', None)
        time_from = self.request.data.get('time_from')
        time_to = self.request.data.get('time_to')

        try:
            user = CustomUser.objects.get(pk=user_pk)

            # day와 date에 맞는 Days 객체를 찾음
            days_queryset = Days.objects.filter(group=user.group_id, day=day)
            days = days_queryset.filter(date=date).first() if date else days_queryset.filter(date__isnull=True).first()

            if not days:
                raise ValidationError("해당 그룹, 요일, 날짜에 일치하는 Days 항목이 없습니다.")

            # 중복 체크
            if Availability.objects.filter(user=user, days=days, time_from=time_from, time_to=time_to).exists():
                raise ValidationError({"detail": "중복된 Availability 데이터가 이미 존재합니다."})

            # 슬롯 업데이트
            current_time = datetime.datetime.strptime(time_from, "%H:%M:%S").time()
            end_time = datetime.datetime.strptime(time_to, "%H:%M:%S").time()

            while current_time < end_time:
                slot, created = Slot.objects.get_or_create(days=days, time=current_time)
                slot.availability_count += 1
                slot.save()
                current_time = (datetime.datetime.combine(datetime.date.today(), current_time) +
                                datetime.timedelta(minutes=30)).time()

            # Availability 인스턴스를 저장하고 Days 정보 포함하여 응답
            availability = serializer.save(user=user, days=days)
            response_serializer = self.get_serializer(availability)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except CustomUser.DoesNotExist:
            raise ValidationError("사용자를 찾을 수 없습니다.")

    def retrieve(self, request, pk=None):
        """
        특정 사용자의 Availability 데이터 조회
        """
        availability_queryset = Availability.objects.filter(user_id=pk)
        if not availability_queryset.exists():
            return Response({"detail": "해당 사용자의 Availability 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(availability_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """
        특정 사용자의 Availability 데이터를 삭제하고 관련 Slot 업데이트
        """
        availability_queryset = Availability.objects.filter(user_id=pk)
        
        if not availability_queryset.exists():
            return Response({"detail": "해당 사용자의 Availability 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        # Slot 데이터 업데이트
        for availability in availability_queryset:
            days = availability.days
            current_time = availability.time_from
            while current_time < availability.time_to:
                slot = Slot.objects.filter(days=days, time=current_time).first()
                if slot:
                    slot.availability_count -= 1
                    if slot.availability_count <= 0:
                        slot.delete()
                    else:
                        slot.save()
                current_time = (datetime.datetime.combine(datetime.date.today(), current_time) +
                                datetime.timedelta(minutes=30)).time()

        availability_queryset.delete()
        return Response({"detail": f"User ID {pk}의 Availability 데이터가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)