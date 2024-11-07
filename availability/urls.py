from django.urls import path, include
from rest_framework import routers
from .views import *

app_name = "availability"

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register("group-timetable", GroupTimetableViewSet, basename="group-timetable")

urlpatterns = [
    path("", include(default_router.urls)),
]