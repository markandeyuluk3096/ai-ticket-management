from rest_framework import serializers
from .models import TicketAIAnalysis


class TicketAIAnalysisSerializer(serializers.ModelSerializer):
    ticket_number = serializers.CharField(source='ticket.ticket_number', read_only=True)

    class Meta:
        model = TicketAIAnalysis
        fields = ['id', 'ticket', 'ticket_number', 'provider', 'model_name', 'result', 'created_at']
        read_only_fields = fields
