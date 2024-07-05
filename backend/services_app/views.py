from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import ServiceAccount
from .serializers import ServiceAccountSerializer, AvitoRegistrationSerializer
from rest_framework.generics import GenericAPIView, ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from django.conf import settings
from utils.avito.avito_functions import (
    get_tokens
)


# Константы для авито (потом надо будет пренести все в специальный файл)
REDIRECT_URI = 'https://hrhub.pixel-team.ru/callback/avito'
CLIENT_ID = settings.CLIENT_ID
CLIENT_SECRET = settings.CLIENT_SECRET
AUTHORIZATION_URL = f'https://www.avito.ru/oauth?response_type=code&client_id={CLIENT_ID}&scope=messenger:read,messenger:write,user:read'


@extend_schema(tags=['ServiceAccount'])
class ServiceAccountCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceAccountSerializer

    def post(self, request, *args, **kwargs):
        allowed_service_names = ['Telegram', 'WhatsApp', 'hh.ru',
                                 'Avito', 'Instagram', 'Facebook', 'vk', 'Yandex Mail']
        service_name = request.data.get('service_name')
        if service_name not in allowed_service_names:
            return Response({"detail": f"Invalid service name. Allowed values are {', '.join(allowed_service_names)}."},
                            status=status.HTTP_400_BAD_REQUEST)

        if ServiceAccount.objects.filter(user_id=request.user.id, service_name=service_name).exists():
            return Response({"detail": "A account with this service already exists for the user."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['ServiceAccount'])
class ServiceAccountListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceAccountSerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return ServiceAccount.objects.filter(user_id=user.id)


@extend_schema(tags=['ServiceAccount'])
class TelegramServiceAccountListView(ListAPIView):
    serializer_class = ServiceAccountSerializer
    pagination_class = None

    def get_queryset(self):
        return ServiceAccount.objects.filter(service_name='Telegram')


@extend_schema(tags=['ServiceAccount'])
class YandexMailServiceAccountListView(ListAPIView):
    serializer_class = ServiceAccountSerializer
    pagination_class = None

    def get_queryset(self):
        return ServiceAccount.objects.filter(service_name='Yandex Mail')


@extend_schema(tags=['ServiceAccount'])
class VKServiceAccountListView(ListAPIView):
    serializer_class = ServiceAccountSerializer
    pagination_class = None

    def get_queryset(self):
        return ServiceAccount.objects.filter(service_name='vk')


class ServiceAccountUpdateView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ServiceAccount.objects.all()
    serializer_class = ServiceAccountSerializer
    lookup_field = 'id'


@extend_schema(tags=['ServiceAccount'])
class ServiceAccountDeleteView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return ServiceAccount.objects.filter(user_id=self.request.user.id)

    def delete(self, request, *args, **kwargs):
        service_account = self.get_object()
        service_account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['ServiceAccount'])
class AvitoRegistrationView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvitoRegistrationSerializer

    @extend_schema(
        description="Получение URL для регистрации аккаунта Avito, нужен для получения authorization_code",
        responses={200: AvitoRegistrationSerializer},
        summary="Получение URL для регистрации аккаунта Avito",
    )
    def get(self, request):
        return Response({"registration_url": AUTHORIZATION_URL}, status=status.HTTP_200_OK)

    @extend_schema(
        description="Регистрация аккаунта по authorization_code",
        responses={200: ServiceAccountSerializer},
        summary="Регистрация аккаунта avito",
    )
    def post(self, request):
        authorization_code = request.data.get('authorization_code')
        print(authorization_code)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            tokens = get_tokens(CLIENT_ID, CLIENT_SECRET, authorization_code)
            print(tokens)
            if isinstance(tokens, int):
                return Response({"detail": "Invalid authorization code."}, status=tokens)
            user = get_user(tokens['access_token'])
            if isinstance(user, int):
                return Response({"detail": "Invalid tokens."}, status=user)
            service_account_serializer = ServiceAccountSerializer(data={
                'service_name': 'Avito',
                'service_username': 'Пока хз',
                'access_token': tokens['access_token'],
                'refresh_token': tokens['refresh_token'],
                'user_id': request.user.id
            }, context={'request': request})

            if service_account_serializer.is_valid(raise_exception=True):
                service_account_serializer.save()
            else:
                return Response(service_account_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(service_account_serializer.data, status=status.HTTP_201_CREATED)
