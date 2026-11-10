"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from USErs.views import CustomerSignUpView
# from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView # Import etemiz

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

urlpatterns = [
    path('admin', admin.site.urls),
    path('api/', include('restaurant.urls')),
    path('api/', include("USErs.urls")),
    path('api/', include('order.urls')),
    path('api/', include('reservation.urls')),

    path('api/auth/login', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/logout', TokenBlacklistView.as_view(), name='token-black-list'),
    path('api/auth/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/register', CustomerSignUpView.as_view(), name='customer-sign-up'),
]


if settings.DEBUG:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView,
    )
    urlpatterns += [
        path('api/schema', SpectacularAPIView.as_view(), name='schema'),
        path('docs', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('redoc', SpectacularRedocView.as_view(url_name='redoc'), name='redoc'),
    ]