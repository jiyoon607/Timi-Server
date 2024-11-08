from django.urls import path, include
from rest_framework import routers
from .views import *

app_name = "result"

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register(r'result', ResultViewSet)

urlpatterns = [
    path('', include(default_router.urls)),
]