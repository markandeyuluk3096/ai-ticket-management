from django.urls import path
from .views import TicketListCreateAPIView, TicketDetailAPIView

urlpatterns = [
    path('', TicketListCreateAPIView.as_view(), name='ticket-list-create'),
    path('<int:pk>/', TicketDetailAPIView.as_view(), name='ticket-detail'),
]
