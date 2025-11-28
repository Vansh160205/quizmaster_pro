"""
QuizMaster Pro - Main URL Configuration
Routes all URLs to appropriate apps
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Include all core app URLs
]