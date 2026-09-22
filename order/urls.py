
from rest_framework.routers import DefaultRouter
from . import views

from django.urls import path, include
router = DefaultRouter()

router.register(r'orders', views.OrderItemView, basename='order')
router.register(r'order_items', views.OrderItemDetailView, basename='order_items')
router.register(r'kitchen/order_items', views.KDSOrderItemViewSet, basename='kitchen')


urlpatterns = [
    path("", include(router.urls)),
]