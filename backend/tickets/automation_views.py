from difflib import SequenceMatcher
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Ticket
from .attachments import TicketAttachment
from .attachment_serializers import TicketAttachmentSerializer


def similarity(left, right):
    return SequenceMatcher(None, left.lower().strip(), right.lower().strip()).ratio()


class SimilarTicketAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        user = request.user
        if user.role != 'admin' and ticket.customer_id != user.id and ticket.assigned_agent_id != user.id:
            raise PermissionDenied('You do not have access to this ticket.')
        candidates = Ticket.objects.filter(category=ticket.category).exclude(pk=ticket.pk).exclude(status__in=[Ticket.Status.CLOSED, Ticket.Status.RESOLVED])
        if user.role == 'customer':
            candidates = candidates.filter(customer=user)
        elif user.role == 'agent':
            candidates = candidates.filter(assigned_agent=user)
        results = []
        for candidate in candidates.only('id', 'ticket_number', 'subject', 'description', 'status')[:200]:
            score = max(similarity(ticket.subject, candidate.subject), similarity(ticket.description[:1000], candidate.description[:1000]))
            if score >= 0.55:
                results.append({'id': candidate.id, 'ticket_number': candidate.ticket_number, 'subject': candidate.subject, 'status': candidate.status, 'similarity': round(score, 2)})
        results.sort(key=lambda item: item['similarity'], reverse=True)
        return Response({'ticket_id': ticket.id, 'possible_duplicates': results[:10]})


class TicketAttachmentListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_ticket(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        user = request.user
        if user.role != 'admin' and ticket.customer_id != user.id and ticket.assigned_agent_id != user.id:
            raise PermissionDenied('You do not have access to this ticket.')
        return ticket

    def get(self, request, ticket_id):
        ticket = self.get_ticket(request, ticket_id)
        files = ticket.attachments.select_related('uploaded_by').all()
        return Response(TicketAttachmentSerializer(files, many=True, context={'request': request}).data)

    def post(self, request, ticket_id):
        ticket = self.get_ticket(request, ticket_id)
        if request.user.role not in ('customer', 'agent', 'admin'):
            raise PermissionDenied('You cannot upload attachments.')
        serializer = TicketAttachmentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        attachment = serializer.save(ticket=ticket, uploaded_by=request.user)
        return Response(TicketAttachmentSerializer(attachment, context={'request': request}).data, status=status.HTTP_201_CREATED)
