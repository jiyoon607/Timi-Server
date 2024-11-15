from rest_framework import serializers
from .models import *
from django.core.exceptions import ObjectDoesNotExist

class CommentSerializer(serializers.ModelSerializer):
    day = serializers.CharField(write_only=True)  # day 필드를 write_only로 추가
    date = serializers.DateField(allow_null=True, required=False, write_only=True)  # date 필드 수정

    # `days`를 직렬화할 때 days의 id와 day, date를 반환하는 `get_days` 메서드 사용
    days = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'

    def create(self, validated_data):
        day = validated_data.pop('day')  # day 값을 가져오기
        date = validated_data.pop('date', None)  # date 값은 없을 수 있으므로 default 값 설정

        user = validated_data.get('user')  # user는 validated_data에 포함되므로 가져옴

        # 사용자의 그룹과 day를 기준으로 days 객체 찾기
        try:
            days_queryset = Days.objects.filter(group=user.group_id, day=day)

            if date:
                # date가 있다면 해당 date로 필터링
                days = days_queryset.filter(date=date).first()
            else:
                # date가 없다면 null인 날짜로 필터링
                days = days_queryset.filter(date__isnull=True).first()

            if not days:
                raise serializers.ValidationError("해당 그룹, 요일, 날짜에 맞는 days 항목이 없습니다.")

            validated_data['days'] = days  # 찾은 days 객체를 validated_data에 추가
            return super().create(validated_data)  # Comment 객체 생성

        except ObjectDoesNotExist:
            raise serializers.ValidationError("일치하는 days 객체가 없습니다.")

    def get_days(self, obj):
        # days 객체의 id, day, date 값을 반환합니다.
        return {
            "id": obj.days.id if obj.days else None,
            "day": obj.days.day if obj.days else None,
            "date": obj.days.date if obj.days else None
        }
