from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import CustomUser, MembersOfGroup

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(
        max_length=None, use_url=True, allow_null=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email',
                  'avatar', 'created_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'is_active']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance, validated_data)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token


class UsernameAndServiceSerializer(serializers.Serializer):
    username = serializers.CharField()
    service = serializers.CharField()


class CustomUserSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    usernames_and_services = serializers.ListField(
        child=UsernameAndServiceSerializer(),
        required=False
        )

    class Meta:
        model = CustomUser
        fields = ['id', 'user', 'profession', 'group_name', 'created_at', 'usernames_and_services']
        read_only_fields = ['id', 'created_at']


class MembersOfGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembersOfGroup
        fields = ['id', 'group', 'user_name_from_message', 'service_name', 'chat_link', 'created_at', 'added']
        read_only_fields = ['id', 'created_at']


class UserUpdateSchema(serializers.Serializer):
    group_name = serializers.CharField(required=False, help_text="Новое название группы")
    profession = serializers.CharField(required=False, help_text="Новая профессия")
    members = serializers.DictField(child=serializers.BooleanField(), required=False, help_text="ID пользователей и флаги true/false")
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['{id}'] = serializers.BooleanField(help_text="ID пользователя и флаг true/false")
