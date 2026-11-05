from rest_framework import generics, permissions
from .models import Ticket
from .permissions import TicketAccessPermission
from .serializers import TicketSerializer, TicketStaffUpdateSerializer


class TicketListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketSerializer

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

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return TicketStaffUpdateSerializer
        return TicketSerializer
