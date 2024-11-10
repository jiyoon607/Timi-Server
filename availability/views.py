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

class AvailiabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer

    def perform_create(self, serializer):
        user_pk = self.request.data.get('user')
        days_pk = self.request.data.get('days')
        time_from = self.request.data.get('time_from')
        time_to = self.request.data.get('time_to')

        try:
            user = CustomUser.objects.get(pk=user_pk)
            days = Days.objects.get(pk=days_pk)
            
            time_from = datetime.datetime.strptime(time_from, "%H:%M:%S").time()
            time_to = datetime.datetime.strptime(time_to, "%H:%M:%S").time()
            
            current_time = time_from
            while current_time < time_to:
                slot = Slot.objects.filter(days=days, time=current_time).first()
                
                if slot:
                    # Slot이 존재하면 availability_count를 증가
                    slot.availability_count += 1
                    slot.save()
                else:
                    # Slot이 없으면 새로 생성
                    Slot.objects.create(
                        days=days,
                        time=current_time,
                        availability_count=1
                    )

                current_time = (datetime.datetime.combine(datetime.date.today(), current_time) +
                                datetime.timedelta(minutes=30)).time()
                
            serializer.save(user=user)  
        except CustomUser.DoesNotExist:
            raise ValidationError("User not found")

    @action(detail=False, methods=['get'], url_path='(?P<user_id>[^/.]+)')
    def list_user_availability(self, request, user_id=None):
        availability_queryset = Availability.objects.filter(user_id=user_id)
        if not availability_queryset.exists():
            return Response({"detail": "No availability data found for this user."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(availability_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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