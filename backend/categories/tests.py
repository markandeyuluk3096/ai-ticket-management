from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Category

User = get_user_model()


class CategoryAPITests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='category_customer', password='StrongPass123!')
        self.category = Category.objects.create(name='Technical', code='TECH')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.customer).access_token}')

    def test_authenticated_user_can_list_active_categories(self):
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['code'], 'TECH')

    def test_inactive_categories_are_hidden(self):
        self.category.is_active = False
        self.category.save()
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], [])
