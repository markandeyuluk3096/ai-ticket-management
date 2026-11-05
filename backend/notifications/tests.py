from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Notification

User = get_user_model()


class NotificationAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='notify_user', password='StrongPass123!')
        self.other = User.objects.create_user(username='notify_other', password='StrongPass123!')
        self.notification = Notification.objects.create(recipient=self.user, title='Ticket update', message='Your ticket changed.')
        Notification.objects.create(recipient=self.other, title='Private', message='Other user notification.')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.user).access_token}')

    def test_user_only_sees_own_notifications(self):
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_user_can_mark_own_notification_read(self):
        response = self.client.patch(f'/api/notifications/{self.notification.pk}/read/', {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_user_cannot_mark_another_users_notification_read(self):
        other_notification = Notification.objects.get(recipient=self.other)
        response = self.client.patch(f'/api/notifications/{other_notification.pk}/read/', {}, format='json')
        self.assertEqual(response.status_code, 404)
