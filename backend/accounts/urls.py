from django.urls import path
from .views import (
    RegisterAPIView,
    CustomLoginAPIView,
    CustomerProfileAPIView,
)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', CustomLoginAPIView.as_view(), name='login'),
    path('profile/', CustomerProfileAPIView.as_view(), name='profile'),
]