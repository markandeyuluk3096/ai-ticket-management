from rest_framework import serializers
from .models import TicketFeedback


class TicketFeedbackSerializer(serializers.ModelSerializer):
    ticket_number = serializers.CharField(source='ticket.ticket_number', read_only=True)

    class Meta:
        model = TicketFeedback
        fields = ['id', 'ticket', 'ticket_number', 'customer', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'ticket', 'ticket_number', 'customer', 'created_at']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value
