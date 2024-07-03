from rest_framework import serializers
from .models import Message
from services_app.models import ServiceAccount


class MessageSerializer(serializers.ModelSerializer):
    account_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Message
        fields = ['id', 'account_id', 'from_username', 'from_userphone', 'text', 'personal_chat_link',
                  'received_at', 'is_read']
        read_only_fields = ['username']

    def create(self, validated_data):
        account_id = validated_data.pop('account_id')
        account = ServiceAccount.objects.get(id=account_id)
        validated_data['account'] = account
        return Message.objects.create(**validated_data)


class MessageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'account', 'from_username', 'from_userphone', 'text', 'personal_chat_link', 'received_at',
                  'is_read']
        read_only_fields = ['id', 'account', 'from_username', 'from_userphone', 'text', 'personal_chat_link',
                            'received_at']
