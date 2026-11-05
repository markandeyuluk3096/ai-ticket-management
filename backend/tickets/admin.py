from django.contrib import admin
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'subject', 'customer', 'category', 'assigned_agent', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('ticket_number', 'subject', 'customer__username', 'customer__email')
    readonly_fields = ('ticket_number', 'created_at', 'updated_at', 'resolved_at')
