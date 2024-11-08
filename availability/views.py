from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from datetime import datetime
from .models import *
from group.models import Group, Days
from .serializers import *
from group.serializers import DaysSerializer
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
        try:
            user = CustomUser.objects.get(pk=user_pk) 
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