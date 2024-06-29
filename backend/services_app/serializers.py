from rest_framework import serializers
from .models import ServiceAccount
from user_app.models import User


class ServiceAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceAccount
        fields = ['id', 'service_name', 'service_username', 'created_at']

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        user = User.objects.get(id=user_id)
        return ServiceAccount.objects.create(user_id=user, **validated_data)
