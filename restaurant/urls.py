from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'restaurants', views.RestaurantViewSet, basename='restaurant')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'dishes', views.DishDetailReceptItemView, basename='dish')
router.register(r'ingredients', views.IngredientDetailStockView, basename='ingredient')
router.register(r'tables', views.TableViewSet, basename='table')

urlpatterns = [
    path("", include(router.urls)),

#     # path('restaurants/', views.RestaurantListCreateView.as_view()),
#     path('restaurants/<int:pk>/', views.RestaurantDetailView.as_view()),

#     path('restaurants/<int:pk>/categories/', views.CategoryListView.as_view()),
#     path('categories/<int:pk>/', views.CategoryDetailView.as_view()),

#     path('categories/<int:pk>/dishes/', views.DishListView.as_view()),
#     path('dishes/<int:pk>/', views.DishDetailView.as_view()),

#     path('dishes/<int:pk>/toggle-availability/', views.DishStoplistView.as_view()),
    
#     path('restaurants/<int:pk>/tables/', views.TableListView.as_view()),

#     path('dish/<int:pk>/recept-items/', views.ReceptItemView.as_view()),

#     path('restaurants/<int:pk>/ingredients/', views.IngredientListView.as_view()),

]