from core import views
from django.urls import path

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('', views.app_info, name='app_info'),
    path('countries/', views.countries, name='countries'),
    path('topics/', views.topics, name='topics'),
    path('sources/', views.sources, name='sources'),
]
