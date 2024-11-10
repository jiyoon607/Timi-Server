from rest_framework import serializers
from .models import *
from group.models import Days
from group.serializers import DaysSerializer

class AvailabilitySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = Availability
        fields = '__all__'

class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = ['availability_count', 'time']

class DaysSlotSerializer(serializers.ModelSerializer):
    slots = SlotSerializer(many=True, read_only=True)  # SlotSerializer를 사용해 days와 연결된 Slot들을 포함

    class Meta:
        model = Days
        fields = ['id', 'day', 'date', 'start_time', 'end_time', 'slots']