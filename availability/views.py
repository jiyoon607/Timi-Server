from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from datetime import datetime
from .models import *
from group.models import Group, Days
from .serializers import *
from group.serializers import DaysSerializer

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
