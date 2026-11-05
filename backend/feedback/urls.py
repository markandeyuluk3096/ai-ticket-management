from django.urls import path
from .views import MyFeedbackListAPIView, TicketFeedbackCreateAPIView

urlpatterns = [
    path('', MyFeedbackListAPIView.as_view(), name='my-feedback'),
    path('tickets/<int:ticket_id>/', TicketFeedbackCreateAPIView.as_view(), name='ticket-feedback-create'),
]
