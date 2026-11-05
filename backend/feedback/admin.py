from django.contrib import admin
from .models import TicketFeedback


@admin.register(TicketFeedback)
class TicketFeedbackAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'customer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('ticket__ticket_number', 'customer__username', 'comment')
    readonly_fields = ('created_at',)
