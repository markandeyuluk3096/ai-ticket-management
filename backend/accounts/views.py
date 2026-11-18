import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework.permissions import IsAuthenticated
from .serializers import ProfileSerializer, CustomTokenObtainPairSerializer, RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenBlacklistView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.exceptions import PermissionDenied

User = get_user_model()


class RegisterAPIView(APIView):
    permission_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'register'

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Customer registered successfully.",
                "user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role}
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomLoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'


class GoogleLoginAPIView(APIView):
    permission_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'google_login'

    def post(self, request):
        client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
        credential = request.data.get('credential')
        if not client_id:
            return Response(
                {'detail': 'Google sign-in is not configured. Set GOOGLE_CLIENT_ID in backend/.env.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        if not credential:
            return Response({'detail': 'A Google credential is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            claims = google_id_token.verify_oauth2_token(
                credential, google_requests.Request(), client_id
            )
        except Exception:
            return Response(
                {'detail': 'The Google credential is invalid or expired.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = (claims.get('email') or '').strip().lower()
        google_sub = claims.get('sub')
        if not email or not google_sub or claims.get('email_verified') is not True:
            return Response(
                {'detail': 'Google must provide a verified email address.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            user = User.objects.filter(google_sub=google_sub).first()
            if user is None:
                user = User.objects.filter(email__iexact=email).first()
                if user is not None:
                    if user.google_sub and user.google_sub != google_sub:
                        return Response(
                            {'detail': 'This account is already linked to another Google identity.'},
                            status=status.HTTP_409_CONFLICT,
                        )
                    user.google_sub = google_sub
                    user.save(update_fields=['google_sub'])
                else:
                    base_username = email.split('@', 1)[0][:120] or 'google_user'
                    username = base_username
                    while User.objects.filter(username=username).exists():
                        username = '{}_{}'.format(base_username[:120], uuid.uuid4().hex[:8])
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        first_name=(claims.get('given_name') or '')[:150],
                        last_name=(claims.get('family_name') or '')[:150],
                        password=uuid.uuid4().hex,
                        role='customer',
                        google_sub=google_sub,
                    )

        if not user.is_active:
            return Response(
                {'detail': 'This account is disabled. Contact support.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        refresh['username'] = user.username
        refresh['role'] = user.role
        return Response(
            {'refresh': str(refresh), 'access': str(refresh.access_token)},
            status=status.HTTP_200_OK,
        )


class AgentListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'admin':
            raise PermissionDenied('Only administrators can view the support-agent directory.')
        agents = User.objects.filter(role='agent', is_active=True).values(
            'id', 'username', 'first_name', 'last_name'
        )
        return Response(list(agents))


class CustomerProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerLogoutAPIView(TokenBlacklistView):
    pass
