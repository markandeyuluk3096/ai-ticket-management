from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from tickets.models import Ticket
from .models import TicketFeedback
from .serializers import TicketFeedbackSerializer


class TicketFeedbackCreateAPIView(generics.CreateAPIView):
    serializer_class = TicketFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        ticket_id = self.kwargs['ticket_id']
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        user = self.request.user
        if user.role != 'customer' or ticket.customer_id != user.id:
            raise PermissionDenied('Only the ticket owner can submit feedback.')
        if ticket.status not in (Ticket.Status.RESOLVED, Ticket.Status.CLOSED):
            raise ValidationError('Feedback can be submitted only after a ticket is resolved or closed.')
        if TicketFeedback.objects.filter(ticket=ticket).exists():
            raise ValidationError('Feedback has already been submitted for this ticket.')
        serializer.save(ticket=ticket, customer=user)


class MyFeedbackListAPIView(generics.ListAPIView):
    serializer_class = TicketFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TicketFeedback.objects.filter(customer=self.request.user).select_related('ticket')
