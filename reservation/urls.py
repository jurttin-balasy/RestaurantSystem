from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register('my_reservations', views.ReservationMe, basename='my_reservation')
router.register('admin_reservations', views.AdminReservationViewSet, basename='admin_reservation')

urlpatterns = [
    path("", include(router.urls)),
]