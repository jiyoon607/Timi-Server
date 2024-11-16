from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Result
from .serializers import ResultSerializer

class ResultViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

    @action(detail=False, methods=["get"], url_path="group/(?P<group_id>[^/.]+)")
    def by_group(self, request, group_id=None):
        """
        특정 그룹 ID에 해당하는 Result 데이터를 반환
        """
        results = self.queryset.filter(group_id=group_id)
        if not results.exists():
            return Response({"detail": "Results not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
