from django.shortcuts import render
from rest_framework import mixins, viewsets
from .models import *
from .serializers import *
# Create your views here.

class CommentViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset=Comment.objects.all()
    serializer_class = CommentSerializer