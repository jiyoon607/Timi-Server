from rest_framework import serializers
from .models import *
from group.models import Days, CustomUser
from group.serializers import DaysSerializer
from django.core.exceptions import ValidationError

class AvailabilitySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    username = serializers.CharField(source='user.name', read_only=True)
    day = serializers.CharField(write_only=True)
    date = serializers.DateField(write_only=True, required=False, allow_null=True)
    group_id = serializers.PrimaryKeyRelatedField(source='user.group_id', read_only=True)

    class Meta:
        model = Availability
        fields = ['id', 'user', 'username', 'group_id', 'day', 'date', 'days', 'time_from', 'time_to']
        extra_kwargs = {
            'days': {'read_only': True}
        }

    def create(self, validated_data):
        day = validated_data.pop('day')
        date = validated_data.pop('date', None)
        user = validated_data['user']
        
        # day, date를 이용해 days 객체 찾기
        days_queryset = Days.objects.filter(group=user.group_id, day=day)
        
        if date:
            days = days_queryset.filter(date=date).first()
        else:
            days = days_queryset.filter(date__isnull=True).first()

        if not days:
            raise ValidationError("No matching Days entry found for the given group, day, and date.")
        
        validated_data['days'] = days
        return super().create(validated_data)

class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = ['availability_count', 'time']

class DaysSlotSerializer(serializers.ModelSerializer):
    slots = SlotSerializer(many=True, read_only=True)  # SlotSerializer를 사용해 days와 연결된 Slot들을 포함

    class Meta:
        model = Days
        fields = ['id', 'day', 'date', 'start_time', 'end_time', 'slots']