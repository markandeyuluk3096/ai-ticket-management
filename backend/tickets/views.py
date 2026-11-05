from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Ticket
from .permissions import TicketAccessPermission
from .serializers import TicketSerializer, TicketStaffUpdateSerializer


class TicketListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketSerializer

    def perform_create(self, serializer):
        if self.request.user.role != 'customer':
            raise PermissionDenied('Only customers can create support tickets.')
        serializer.save()

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Ticket.objects.select_related('category', 'customer', 'assigned_agent')
        if user.role == 'agent':
            return Ticket.objects.filter(assigned_agent=user).select_related('category', 'customer', 'assigned_agent')
        return Ticket.objects.filter(customer=user).select_related('category', 'customer', 'assigned_agent')


class TicketDetailAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, TicketAccessPermission]
    queryset = Ticket.objects.select_related('category', 'customer', 'assigned_agent')

    def perform_update(self, serializer):
        ticket = serializer.save()
        if ticket.status in (Ticket.Status.RESOLVED, Ticket.Status.CLOSED) and ticket.resolved_at is None:
            ticket.resolved_at = timezone.now()
            ticket.save(update_fields=['resolved_at', 'updated_at'])
        elif ticket.status not in (Ticket.Status.RESOLVED, Ticket.Status.CLOSED) and ticket.resolved_at is not None:
            ticket.resolved_at = None
            ticket.save(update_fields=['resolved_at', 'updated_at'])

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return TicketStaffUpdateSerializer
        return TicketSerializer
