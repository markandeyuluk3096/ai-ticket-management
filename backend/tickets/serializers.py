from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from categories.models import Category
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category', queryset=Category.objects.filter(is_active=True), write_only=True
    )
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    assigned_agent_username = serializers.CharField(source='assigned_agent.username', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'subject', 'description', 'category_id',
            'category_name', 'customer', 'customer_username', 'assigned_agent',
            'assigned_agent_username', 'status', 'priority', 'created_at',
            'updated_at', 'resolved_at',
        ]
        read_only_fields = [
            'id', 'ticket_number', 'customer', 'customer_username',
            'assigned_agent', 'assigned_agent_username', 'status', 'priority',
            'created_at', 'updated_at', 'resolved_at',
        ]

    def create(self, validated_data):
        category = validated_data.pop('category')
        with transaction.atomic():
            locked_category = Category.objects.select_for_update().get(pk=category.pk)
            sequence = locked_category.next_ticket_number
            locked_category.next_ticket_number = sequence + 1
            locked_category.save(update_fields=['next_ticket_number'])
            ticket_number = f'{locked_category.code}-{timezone.localdate().year}-{sequence:04d}'
            return Ticket.objects.create(
                category=locked_category,
                ticket_number=ticket_number,
                customer=self.context['request'].user,
                **validated_data,
            )


class TicketStaffUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['status', 'priority', 'assigned_agent']

    def validate_assigned_agent(self, user):
        if user and user.role not in ('agent', 'admin'):
            raise serializers.ValidationError('Tickets can only be assigned to a support agent or administrator.')
        return user
