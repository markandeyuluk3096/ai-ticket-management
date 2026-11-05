from rest_framework import generics, permissions
from tickets.models import Ticket
from .models import Message
from .serializers import MessageSerializer


class TicketMessageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_ticket(self):
        user = self.request.user
        ticket = generics.get_object_or_404(Ticket, pk=self.kwargs['ticket_id'])
        if user.role != 'admin' and ticket.customer_id != user.id and ticket.assigned_agent_id != user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You do not have access to this ticket conversation.')
        return ticket

    def get_queryset(self):
        return Message.objects.filter(ticket=self.get_ticket()).select_related('sender')

    def perform_create(self, serializer):
        serializer.save(ticket=self.get_ticket(), sender=self.request.user)
