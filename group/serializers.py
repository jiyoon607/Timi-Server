from rest_framework import serializers
from .models import *

class DaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Days
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    group_id = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = CustomUser
        fields = '__all__'