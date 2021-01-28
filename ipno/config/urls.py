"""ipno URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf import settings
from django.urls import re_path, include, path

from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from departments.views import DepartmentsViewSet
from documents.views import DocumentsViewSet
from app_config.views import AppConfigViewSet
from analytics.views import AnalyticsViewSet
from officers.views import OfficersViewSet

api_router = routers.SimpleRouter()

api_router.register(r'documents', DocumentsViewSet, basename='documents')
api_router.register(r'departments', DepartmentsViewSet, basename='departments')
api_router.register(r'app-config', AppConfigViewSet, basename='app-config')
api_router.register(r'analytics', AnalyticsViewSet, basename='analytics')
api_router.register(r'officers', OfficersViewSet, basename='officers')

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^api/', include((api_router.urls, 'api'), namespace='api')),
    path('api/token/', TokenObtainPairView.as_view(), name='token'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
