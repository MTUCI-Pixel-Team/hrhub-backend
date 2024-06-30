from rest_framework import serializers
from .models import Message
from services_app.models import ServiceAccount


class MessageSerializer(serializers.ModelSerializer):
    account_id = serializers.IntegerField(source='account.id', read_only=True)
    username = serializers.SlugRelatedField(source='account.user_id', slug_field='username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'account_id', 'username', 'from_username', 'from_userphone', 'text', 'personal_chat_link',
                  'received_at', 'is_read']
        read_only_fields = ['account']

    def create(self, validated_data):
        request = self.context.get('request')
        account = ServiceAccount.objects.get(user_id=request.user.id)
        return Message.objects.create(account=account, **validated_data)


class MessageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'account', 'from_username', 'from_userphone', 'text', 'personal_chat_link', 'received_at',
                  'is_read']
        read_only_fields = ['id', 'account', 'from_username', 'from_userphone', 'text', 'personal_chat_link',
                            'received_at']
