from django.urls import path
from .chat_views import ChatMessageAPIView, ChatSessionDetailAPIView, ChatSessionListAPIView

urlpatterns = [
    path('chat/', ChatMessageAPIView.as_view(), name='ai-chat'),
    path('chat/sessions/', ChatSessionListAPIView.as_view(), name='ai-chat-sessions'),
    path('chat/sessions/<int:pk>/', ChatSessionDetailAPIView.as_view(), name='ai-chat-session-detail'),
]
