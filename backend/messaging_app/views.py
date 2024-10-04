import json
from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Message
from .serializers import MessageSerializer, MessageUpdateSerializer
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import DestroyAPIView, UpdateAPIView
from services_app.models import ServiceAccount
from django.views.decorators.csrf import csrf_exempt
from utils.avito.avito_functions import set_webhook, get_chats, read_message
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from user_app.models import User
from django.views.generic import TemplateView
from utils.websocket.websocket_functions import send_message_to_user
from user_app.models import CustomUser, MembersOfGroup
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import FieldDoesNotExist


@extend_schema(tags=['Message'])
class MessageCreateView(GenericAPIView):
    serializer_class = MessageSerializer

    def post(self, request, *args, **kwargs):
        account_id = request.data.get('account_id')
        if not account_id:
            return Response({"error": "account_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            account = ServiceAccount.objects.get(id=account_id)
        except ServiceAccount.DoesNotExist:
            return Response({"error": "ServiceAccount not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(account=account)
            send_message_to_user(account.user_id_id, serializer.data, account.service_name)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Message'])
class MessageListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(account__user_id=user.id).order_by('-received_at')


@extend_schema(tags=['Message'])
class MessageDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field = 'id'


@extend_schema(tags=['Message'])
class MessageUpdateView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all()
    serializer_class = MessageUpdateSerializer
    lookup_field = 'id'


@extend_schema(tags=['Message'])
class UnreadMessageListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(account__user_id=user.id, is_read=False)


@csrf_exempt
def avito_webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body).get('payload')
            if data.get('type') == 'message':
                user_id = data.get('value').get('user_id')
                service_account = get_object_or_404(ServiceAccount, service_user_id=user_id)
                user = get_object_or_404(User, id=service_account.user_id_id)
                chats = get_chats(user.id).get('chats')
                chats_info = []

                for chat in chats:
                    text = chat.get('last_message').get('content').get('text')
                    chat_id = chat.get('id')
                    for chat_partner in chat.get('users'):
                        if chat_partner.get('id') != user_id:
                            chats_info.append({
                                'from_username': chat_partner.get('name'),
                                'personal_chat_link': chat_partner.get('public_user_profile').get('url'),
                                'text': text,
                                'chat_id': chat_id
                            })
                            break

                for chat_info in chats_info:
                    message_serializer = MessageSerializer(data={
                        'account_id': service_account.id,
                        'from_username': chat_info.get('from_username'),
                        'text': chat_info.get('text'),
                        'personal_chat_link': chat_info.get('personal_chat_link')
                    })
                    if message_serializer.is_valid():
                        message_serializer.save()
                        read_message(user.id, chat_info.get('chat_id'))

                        send_message_to_user(user.id, message_serializer.data, 'avito')

                return HttpResponse(status=200)
            else:
                return HttpResponse(status=204)

        except json.JSONDecodeError:
            return HttpResponse(status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(
    tags=['ServiceAccount'],
    description="Подключает пользователя к вебхуку уведомлений Avito. Это позволяет получать сообщения в реальном времени.",
    responses={200: {"ok": "True"}},
    summary="Подключение вебхука для Avito",
)
def register_avito_webhook(request):
    user = request.user
    token = get_object_or_404(ServiceAccount, user_id=user.id, service_name='Avito').access_token
    if user and token:
        url = 'https://hrhub.pixel-team.ru/api/message/avito_webhook/'
        response = set_webhook(token, url)
        return Response(response)
    else:
        return Response({"User or token not found"}, status=status.HTTP_404_NOT_FOUND)


class WebSocketTestView(TemplateView):
    template_name = 'messaging_app/websocket_test.html'


@extend_schema(tags=['Message'])
class MessageListForPeoplesView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    class MessagePagination(PageNumberPagination):
        page_size = 20
        page_size_query_param = 'page_size'
        max_page_size = 100

    @extend_schema(
        description="Получения сообщений для группы",
        responses={
            status.HTTP_200_OK: MessageSerializer,
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Нет прав для выполнения операции"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Группа не найдена")
        },
        parameters=[
            OpenApiParameter(
                name='sort',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Поле для сортировки. Допустимые значения: 'received_at', 'from_username', 'account'. Можно добавить '-' перед значением для сортировки в обратном порядке.",
                required=False
            ),
        ],
        summary="Получения сообщений для группы",
    )
    def get(self, request, *args, **kwargs):
        group_id = kwargs.get('id')
        sort = request.GET.get('sort')
        allowed_fields = ['received_at', 'from_username', 'account']

        group = get_object_or_404(CustomUser, id=group_id)
        user = self.request.user
        if group.user != user:
            return Response({"detail": "Нет прав для выполнения операции"}, status=status.HTTP_403_FORBIDDEN)
        members_of_group = MembersOfGroup.objects.filter(group=group)
        messages_query = Message.objects.none()

        for member in members_of_group:
            if member.added:
                messages_query = messages_query | Message.objects.filter(
                    from_username=member.user_name_from_message,
                    personal_chat_link=member.chat_link
                )

        if sort:
            if sort.startswith('-'):
                sort_field = sort[1:]
                reverse = True
            else:
                sort_field = sort
                reverse = False
            if sort_field in allowed_fields:
                try:
                    Message._meta.get_field(sort_field)
                    if reverse:
                        sorted_messages = messages_query.order_by(f'-{sort_field}')
                    else:
                        sorted_messages = messages_query.order_by(sort_field)
                except FieldDoesNotExist:
                    pass
        else:
            sorted_messages = messages_query.order_by('received_at')

        paginator = self.MessagePagination()
        page = paginator.paginate_queryset(sorted_messages, request)
        serializer = self.get_serializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
