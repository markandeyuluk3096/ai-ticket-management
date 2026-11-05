from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()


class CustomerRegistrationSecurityTests(APITestCase):
    url = '/api/accounts/register/'

    def setUp(self):
        # Keep registration tests independent of cached throttle counters.
        cache.clear()

    def test_registration_requires_email(self):
        response = self.client.post(self.url, {
            'username': 'new_customer',
            'password': 'A-Long-Random-Password-2026!',
            'confirm_password': 'A-Long-Random-Password-2026!',
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)

    def test_registration_rejects_common_password(self):
        response = self.client.post(self.url, {
            'username': 'new_customer',
            'email': 'new@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
        self.assertFalse(User.objects.filter(username='new_customer').exists())

    def test_registration_accepts_valid_password_and_sets_customer_role(self):
        password = 'Violet-River!2026-Strong'
        response = self.client.post(self.url, {
            'username': 'new_customer',
            'email': 'new@example.com',
            'password': password,
            'confirm_password': password,
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        user = User.objects.get(username='new_customer')
        self.assertEqual(user.role, 'customer')
        self.assertTrue(user.check_password(password))


class SuperuserRoleTests(APITestCase):
    def test_new_superuser_receives_admin_application_role(self):
        admin = User.objects.create_superuser(
            username='role_admin',
            email='role-admin@example.com',
            password='Strong-Admin-Password-2026!',
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertEqual(admin.role, 'admin')

    def test_superuser_role_cannot_be_saved_as_customer(self):
        admin = User.objects.create_superuser(
            username='role_admin_two',
            email='role-admin-two@example.com',
            password='Strong-Admin-Password-2026!',
        )
        admin.role = 'customer'
        admin.save()
        admin.refresh_from_db()
        self.assertEqual(admin.role, 'admin')


class AuthenticationRateLimitTests(APITestCase):
    def setUp(self):
        cache.clear()

    def test_registration_is_limited_to_five_requests_per_hour(self):
        payload = {
            'username': 'rate_limited_customer',
            'email': 'rate-limited@example.com',
            'password': 'Violet-River!2026-Strong',
            'confirm_password': 'Violet-River!2026-Strong',
        }
        for _ in range(5):
            self.client.post('/api/accounts/register/', payload, format='json')

        response = self.client.post('/api/accounts/register/', payload, format='json')
        self.assertEqual(response.status_code, 429)

    def test_login_is_limited_to_ten_requests_per_minute(self):
        payload = {'username': 'unknown-user', 'password': 'Wrong-Password-2026!'}
        for _ in range(10):
            self.client.post('/api/accounts/login/', payload, format='json')

        response = self.client.post('/api/accounts/login/', payload, format='json')
        self.assertEqual(response.status_code, 429)
