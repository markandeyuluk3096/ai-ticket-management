from pathlib import Path
from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'ticket', 'sender', 'sender_username', 'body', 'attachment', 'created_at']
        read_only_fields = ['id', 'ticket', 'sender', 'sender_username', 'created_at']

    def validate(self, attrs):
        body = attrs.get('body', '')
        attachment = attrs.get('attachment')
        if not body.strip() and not attachment:
            raise serializers.ValidationError('A message must contain text or an attachment.')
        if attachment:
            if attachment.size > 5 * 1024 * 1024:
                raise serializers.ValidationError({'attachment': 'Maximum attachment size is 5 MB.'})
            allowed = {'.pdf', '.png', '.jpg', '.jpeg', '.txt', '.docx'}
            if Path(attachment.name).suffix.lower() not in allowed:
                raise serializers.ValidationError({'attachment': 'Unsupported file type.'})
        return attrs
