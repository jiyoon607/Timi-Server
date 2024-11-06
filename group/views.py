from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from .models import *
from .serializers import *

# Create your views here.
class CreateGroupViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = GroupSerializer

    def create(self, request, *args, **kwargs):
        group_data = {
            'name': request.data.get('name')
        }
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        
        group_serializer = self.get_serializer(data=group_data)
        group_serializer.is_valid(raise_exception=True)
        group = group_serializer.save()

        # Days 데이터 추출 및 생성
        days_list = request.data.get('days', [])
        created_days = []
        
        for days in days_list:
            days_data = {
                'group': group.id,
                'day': days['day'],
                'date': days.get('date'),
                'start_time': start_time,
                'end_time': end_time
            }
            days_serializer = DaysSerializer(data=days_data)
            days_serializer.is_valid(raise_exception=True)
            days_serializer.save()
            created_days.append(days_serializer.data)
        
        response_data = group_serializer.data
        response_data['days'] = created_days
        return Response(response_data, status=status.HTTP_201_CREATED)