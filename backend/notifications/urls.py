from django.urls import path
from .views import NotificationListAPIView, NotificationReadAPIView

urlpatterns = [
    path('', NotificationListAPIView.as_view(), name='notification-list'),
    path('<int:pk>/read/', NotificationReadAPIView.as_view(), name='notification-read'),
]
