from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from datetime import datetime
from .models import *
from .serializers import *
from rest_framework.decorators import api_view
# Create your views here.
class GroupViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin):
    serializer_class = GroupSerializer

    def get_queryset(self):
        return Group.objects.all()

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

    @action(methods=["GET"], detail=False)
    def today(self, request):
        today = datetime.datetime.today()
        print(today)
        data = []
        plus = datetime.timedelta(days=1)
        for i in range(0, 35):
            temp_day = today + plus * i
            temp_data = {
                'year': temp_day.year,
                'month': temp_day.month,
                'day': temp_day.day,
                'weekday': temp_day.strftime("%a")
            }
            data.append(temp_data)  # 수정된 부분
        return Response(data)
    

@api_view(['POST'])
def customuser_create(request, group_id):
    if request.method == 'POST':
        data = request.data.copy()  # 요청 데이터를 복사
        serializer = CustomUserSerializer(data=data, context={'request': request})
        
        if serializer.is_valid(raise_exception=True):
            # save() 메서드에서 group_id를 설정하여 저장
            serializer.save(group_id_id=group_id)
            return Response(data=serializer.data)
