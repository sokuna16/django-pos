
from django.urls import path
from .import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('create/', views.create_post, name='create_post'),
]