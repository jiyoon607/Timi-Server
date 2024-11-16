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
        if time_from == '24:00:00':
            time_from = datetime.time(23, 59, 59)
        if time_to == '24:00:00':
            time_to = datetime.time(23, 59, 59)
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
            return Response({"detail": "해당 사용자의 Availability 데이터가 없습니다."})
        
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
    
    @action(detail=False, methods=['post'])
    def availabilitydetail(self, request):
        group = request.data.get('group')
        day = request.data.get('day')
        date = request.data.get('date')
        time = request.data.get('time')

        if not all([group, day, time]):
            return Response({"error": "group, day, and time are required."}, status=status.HTTP_400_BAD_REQUEST)

        days = get_object_or_404(Days, group=group, day=day, date=date)
        day_availabilitys = Availability.objects.filter(days=days)
        time_availabilitys = day_availabilitys.filter(time_from__lte=time, time_to__gt=time)
        group_users = CustomUser.objects.filter(group_id=group)

        available_user = []
        unavailable_user = []
        for user in group_users:
            if time_availabilitys.filter(user=user).exists():
                available_user.append(user.name)
            else:
                unavailable_user.append(user.name)

        comments = Comment.objects.filter(days=days, time=time)

        comments_data = []
        for comment in comments:
            comments_data.append({
                'id': comment.id,
                'user':comment.user.name,
                'text':comment.text,
                'created_at':comment.created_at
            })
        data = {
            'available_user':available_user,
            'unavailable_user':unavailable_user,
            'comments_data':comments_data
        }
        return Response(data, status=status.HTTP_200_OK)