from django.urls import path
from .views import TicketAIAnalysisAPIView, TicketAIAnalysisHistoryAPIView

urlpatterns = [
    path('tickets/<int:ticket_id>/analyze/', TicketAIAnalysisAPIView.as_view(), name='ticket-ai-analyze'),
    path('tickets/<int:ticket_id>/analyses/', TicketAIAnalysisHistoryAPIView.as_view(), name='ticket-ai-analysis-history'),
]
