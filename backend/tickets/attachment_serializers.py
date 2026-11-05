from pathlib import Path
from rest_framework import serializers
from .attachments import TicketAttachment


class TicketAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAttachment
        fields = ['id', 'ticket', 'uploaded_by', 'file', 'original_name', 'uploaded_at']
        read_only_fields = ['id', 'ticket', 'uploaded_by', 'original_name', 'uploaded_at']

    def validate_file(self, value):
        from .attachments import validate_attachment
        validate_attachment(value)
        return value

    def create(self, validated_data):
        uploaded_file = validated_data['file']
        validated_data['original_name'] = Path(uploaded_file.name).name[:255]
        return super().create(validated_data)
