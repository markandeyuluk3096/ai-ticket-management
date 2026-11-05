from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle
from categories.models import Category
from tickets.models import Ticket
from .models import TicketAIAnalysis
from .serializers import TicketAIAnalysisSerializer
from .services import AIServiceError, analyze_ticket


class AIAnalysisThrottle(UserRateThrottle):
    scope = 'ai_analysis'


class TicketAIAnalysisAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [AIAnalysisThrottle]

    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        user = request.user
        if user.role != 'admin' and ticket.customer_id != user.id and ticket.assigned_agent_id != user.id:
            raise PermissionDenied('You do not have access to this ticket.')
        categories = list(Category.objects.filter(is_active=True).order_by('name'))
        try:
            result = analyze_ticket(ticket, categories)
        except AIServiceError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        analysis = TicketAIAnalysis.objects.create(
            ticket=ticket,
            requested_by=user,
            model_name=getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini'),
            result=result,
        )
        return Response(TicketAIAnalysisSerializer(analysis).data, status=status.HTTP_201_CREATED)


class TicketAIAnalysisHistoryAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        user = request.user
        if user.role != 'admin' and ticket.customer_id != user.id and ticket.assigned_agent_id != user.id:
            raise PermissionDenied('You do not have access to this ticket.')
        analyses = TicketAIAnalysis.objects.filter(ticket=ticket)
        return Response(TicketAIAnalysisSerializer(analyses, many=True).data)
