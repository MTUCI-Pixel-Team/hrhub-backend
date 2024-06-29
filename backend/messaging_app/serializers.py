from rest_framework import serializers
from .models import Message
from services_app.models import ServiceAccount


class MessageSerializer(serializers.ModelSerializer):
    account_id = serializers.IntegerField(source='account.id')

    class Meta:
        model = Message
        fields = ['id', 'account_id', 'from_username', 'from_userphone', 'text', 'received_at']
        read_only_fields = ['account']

    def create(self, validated_data):
        account_id = validated_data.pop('account_id')
        account = ServiceAccount.objects.get(id=account_id)
        return Message.objects.create(account=account, **validated_data)
