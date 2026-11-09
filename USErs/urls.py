from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path, include

router = DefaultRouter(trailing_slash=False)
router.register(r'admins', views.RestoranAdminViewSet, basename='adminler')
router.register(r'staff', views.XizmetkerDetailView, basename='staff')
router.register(r'users', views.UserView, basename='user')

urlpatterns = [
    # Mijoz ro'yxatdan o'tishi uchun maxsus URL
    # path('/sign_up/', views.CustomerSignUpView.as_view(), name='customer-sign-up'),

    # Qolgan router URL lari
    path('', include(router.urls)),

]