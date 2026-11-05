from django.urls import path
from .views import TicketMessageListCreateAPIView

urlpatterns = [
    path('tickets/<int:ticket_id>/messages/', TicketMessageListCreateAPIView.as_view(), name='ticket-messages'),
]
