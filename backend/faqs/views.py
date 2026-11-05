from rest_framework import generics, permissions, filters
from .models import FAQ
from .serializers import FAQSerializer


class FAQListAPIView(generics.ListAPIView):
    serializer_class = FAQSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = FAQ.objects.filter(is_published=True).select_related('category')
    filter_backends = [filters.SearchFilter]
    search_fields = ['question', 'answer', 'category__name']
