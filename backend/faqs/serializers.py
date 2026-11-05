from rest_framework import serializers
from .models import FAQ


class FAQSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category', 'category_name', 'updated_at']
        read_only_fields = fields
