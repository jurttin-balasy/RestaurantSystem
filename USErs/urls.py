from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path, include

router = DefaultRouter()
router.register(r'adminler', views.RestoranAdminViewSet, basename='adminler')
router.register(r'customers', views.CustomerListView, basename='customer')

urlpatterns = [
    # Mijoz ro'yxatdan o'tishi uchun maxsus URL
    # path('/sign_up/', views.CustomerSignUpView.as_view(), name='customer-sign-up'),

    # Qolgan router URL lari
    path('', include(router.urls)),

]