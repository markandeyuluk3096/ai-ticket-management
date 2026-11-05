from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .models import FAQ

User = get_user_model()


class FAQAPITests(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username='faq_reader', password='StrongPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(user).access_token}')
        FAQ.objects.create(question='How do I reset my password?', answer='Use the password reset link.', is_published=True)
        FAQ.objects.create(question='Internal draft', answer='Not public.', is_published=False)

    def test_only_published_faqs_are_listed(self):
        response = self.client.get('/api/faqs/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_faq_search(self):
        response = self.client.get('/api/faqs/?search=password')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
