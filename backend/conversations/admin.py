from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'sender', 'created_at')
    search_fields = ('ticket__ticket_number', 'sender__username', 'body')
    readonly_fields = ('created_at',)
