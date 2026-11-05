from django.contrib import admin
from .models import TicketAIAnalysis


@admin.register(TicketAIAnalysis)
class TicketAIAnalysisAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'requested_by', 'model_name', 'created_at')
    list_filter = ('model_name', 'created_at')
    search_fields = ('ticket__ticket_number', 'requested_by__username')
    readonly_fields = ('ticket', 'requested_by', 'provider', 'model_name', 'result', 'created_at')


from .models import ChatMessage, ChatSession


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'created_at', 'updated_at')
    search_fields = ('user__username', 'title')
    readonly_fields = ('user', 'title', 'created_at', 'updated_at')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content', 'session__user__username')
    readonly_fields = ('session', 'role', 'content', 'source_faqs', 'created_at')
