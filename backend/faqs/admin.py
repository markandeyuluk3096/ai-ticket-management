from django.contrib import admin
from .models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_published', 'updated_at')
    list_filter = ('is_published', 'category')
    search_fields = ('question', 'answer')
