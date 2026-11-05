from django.urls import path
from .automation_views import SimilarTicketAPIView, TicketAttachmentListCreateAPIView

urlpatterns = [
    path('<int:ticket_id>/similar/', SimilarTicketAPIView.as_view(), name='ticket-similar'),
    path('<int:ticket_id>/attachments/', TicketAttachmentListCreateAPIView.as_view(), name='ticket-attachments'),
]
