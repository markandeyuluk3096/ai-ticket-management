from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle
from .chatbot import generate_chat_answer, retrieve_faq_context
from .models import ChatMessage, ChatSession
from .chat_serializers import ChatRequestSerializer, ChatSessionSerializer
from .services import AIServiceError


class ChatbotThrottle(UserRateThrottle):
    scope = 'ai_chat'


class ChatSessionListAPIView(generics.ListAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).prefetch_related('messages')


class ChatMessageAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ChatbotThrottle]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')
        if session_id:
            session = get_object_or_404(ChatSession, pk=session_id, user=request.user)
        else:
            session = ChatSession.objects.create(user=request.user, title=message[:120])
        history = list(session.messages.order_by('-created_at').values('role', 'content')[:8])
        history.reverse()
        faqs = retrieve_faq_context(message)
        try:
            answer = generate_chat_answer(message, history, faqs)
        except AIServiceError as exc:
            if not session.messages.exists():
                session.delete()
            return Response({'detail': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        ChatMessage.objects.create(session=session, role=ChatMessage.Role.USER, content=message)
        sources = [{'id': faq.id, 'question': faq.question} for faq in faqs]
        reply = ChatMessage.objects.create(session=session, role=ChatMessage.Role.ASSISTANT, content=answer, source_faqs=sources)
        session.updated_at = timezone.now()
        session.save(update_fields=['updated_at'])
        return Response({'session_id': session.id, 'message': {'id': reply.id, 'role': reply.role, 'content': reply.content, 'source_faqs': reply.source_faqs, 'created_at': reply.created_at}}, status=status.HTTP_200_OK)


class ChatSessionDetailAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).prefetch_related('messages')
