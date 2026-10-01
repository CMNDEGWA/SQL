from django.urls import path
from .views import inventory_dashboard

urlpatterns = [
    path('', inventory_dashboard, name='dashboard'),
]