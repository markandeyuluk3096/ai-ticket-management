from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'next_ticket_number')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
