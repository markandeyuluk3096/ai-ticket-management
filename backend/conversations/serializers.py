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
        return attrs
