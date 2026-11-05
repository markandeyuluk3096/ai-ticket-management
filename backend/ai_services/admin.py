from django.contrib import admin
from .models import TicketAIAnalysis


@admin.register(TicketAIAnalysis)
class TicketAIAnalysisAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'requested_by', 'model_name', 'created_at')
    list_filter = ('model_name', 'created_at')
    search_fields = ('ticket__ticket_number', 'requested_by__username')
    readonly_fields = ('ticket', 'requested_by', 'provider', 'model_name', 'result', 'created_at')
