from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter(trailing_slash=False)

router.register('reservations', views.ReservationMe, basename='my_reservation')
router.register('reservations', views.AdminReservationViewSet, basename='admin_reservation')

urlpatterns = [
    path("", include(router.urls)),
]