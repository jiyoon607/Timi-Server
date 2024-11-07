from django.urls import path, include
from rest_framework import routers
from .views import *

app_name = "group"

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register("group", GroupViewSet, basename="group")

urlpatterns = [
    path("", include(default_router.urls))
]