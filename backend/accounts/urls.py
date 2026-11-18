from django.urls import path
from .views import (
    RegisterAPIView,
    CustomLoginAPIView,
    GoogleLoginAPIView,
    AgentListAPIView,
    CustomerProfileAPIView,
    CustomerLogoutAPIView,
)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', CustomLoginAPIView.as_view(), name='login'),
    path('google/', GoogleLoginAPIView.as_view(), name='google-login'),
    path('agents/', AgentListAPIView.as_view(), name='agent-list'),
    path('profile/', CustomerProfileAPIView.as_view(), name='profile'),
    path('logout/', CustomerLogoutAPIView.as_view(), name='logout'),
]