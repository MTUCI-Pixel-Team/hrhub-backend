from rest_framework import serializers
from .models import ServiceAccount
from user_app.models import User


class ServiceAccountSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user_id.id')
    access_token = serializers.CharField(write_only=True, required=False)
    refresh_token = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = ServiceAccount
        fields = ['id', 'user_id', 'service_name',
                  'service_username', 'email', 'app_password', 'created_at',
                  'access_token', 'refresh_token']

    def validate(self, data):
        if data['service_name'].lower() == 'yandex mail':
            if not data.get('email') or not data.get('app_password'):
                raise serializers.ValidationError(
                    "Email and app_password are required for Yandex Mail service.")
        return data

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        user = User.objects.get(id=user_id)
        return ServiceAccount.objects.create(user_id=user, **validated_data)


class AvitoRegistrationSerializer(serializers.Serializer):
    authorization_code = serializers.CharField(max_length=255)
