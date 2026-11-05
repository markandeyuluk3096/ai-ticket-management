from rest_framework import generics, permissions
from .models import Category
from .serializers import CategorySerializer


class CategoryListAPIView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.objects.filter(is_active=True)
