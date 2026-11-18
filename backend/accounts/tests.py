from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken

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


from unittest.mock import patch
from django.test import override_settings


class GoogleLoginAPITests(APITestCase):
    url = '/api/accounts/google/'

    def setUp(self):
        cache.clear()

    @patch('accounts.views.google_id_token.verify_oauth2_token')
    @override_settings(GOOGLE_CLIENT_ID='test-google-client.apps.googleusercontent.com')
    def test_verified_google_user_can_sign_in(self, verify_token):
        verify_token.return_value = {
            'sub': 'google-sub-123',
            'email': 'google.user@example.com',
            'email_verified': True,
            'given_name': 'Google',
            'family_name': 'User',
        }
        response = self.client.post(self.url, {'credential': 'valid-test-token'}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        user = User.objects.get(email='google.user@example.com')
        self.assertEqual(user.role, 'customer')
        self.assertEqual(user.google_sub, 'google-sub-123')

    @patch('accounts.views.google_id_token.verify_oauth2_token')
    @override_settings(GOOGLE_CLIENT_ID='test-google-client.apps.googleusercontent.com')
    def test_unverified_google_email_is_rejected(self, verify_token):
        verify_token.return_value = {
            'sub': 'google-sub-unverified',
            'email': 'unverified@example.com',
            'email_verified': False,
        }
        response = self.client.post(self.url, {'credential': 'unverified-token'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(email='unverified@example.com').exists())

    @override_settings(GOOGLE_CLIENT_ID='')
    def test_google_sign_in_requires_server_client_id(self):
        response = self.client.post(self.url, {'credential': 'token'}, format='json')
        self.assertEqual(response.status_code, 503)


class AgentDirectoryAPITests(APITestCase):
    def test_only_admin_can_list_support_agents(self):
        agent = User.objects.create_user(username='directory_agent', password='StrongPass123!', role='agent')
        customer = User.objects.create_user(username='directory_customer', password='StrongPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(customer).access_token}')
        denied = self.client.get('/api/accounts/agents/')
        self.assertEqual(denied.status_code, 403)

        admin = User.objects.create_user(username='directory_admin', password='StrongPass123!', role='admin')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(admin).access_token}')
        allowed = self.client.get('/api/accounts/agents/')
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual([item['id'] for item in allowed.data], [agent.id])
