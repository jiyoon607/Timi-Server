from django.urls import path, include
from rest_framework import routers
from .views import *

app_name = "availability"

default_router = routers.SimpleRouter(trailing_slash=False)
default_router.register("group-timetable", GroupTimetableViewSet, basename="group-timetable")
default_router.register("availability", AvailabilityViewSet, basename="availability")

urlpatterns = [
    path("", include(default_router.urls)),
    path('availability/<int:user_id>/', AvailabilityViewSet.as_view({'get': 'list_user_availability'}), name='user-availability'),
]