from django.urls import path
from .views import RegisterAPIView, CustomLoginAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', CustomLoginAPIView.as_view(), name='login'),
]