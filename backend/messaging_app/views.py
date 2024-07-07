from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Message
from .serializers import MessageSerializer, MessageUpdateSerializer
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import DestroyAPIView, UpdateAPIView
from services_app.models import ServiceAccount
from django.views.decorators.csrf import csrf_exempt
import json
from utils.avito.avito_functions import set_webhook
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.http import HttpResponse


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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Message'])
class MessageListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(account__user_id=user.id)


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
@extend_schema(tags=['Message'])
def webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body).get('payload')
            if data.get('type') == 'message':
                message_info = data.get('value')
                print("Получено сообщение от Webhook:", message_info)
                user_id = message_info.get('user_id')
                author_id = message_info.get('author_id')
                chat_id = message_info.get('chat_id')
                text = message_info.get('content').get('text')
                print("user_id:", user_id)
                print("author_id:", author_id)
                print("chat_id:", chat_id)
                print("text:", text)
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=204)
        except json.JSONDecodeError:
            return HttpResponse(status=400)


@api_view(['POST'])
@extend_schema(tags=['Message'])
def register_webhook(request):
    user = request.user
    token = get_object_or_404(ServiceAccount, user_id=user.id).access_token
    if user and token:
        response = set_webhook(token, 'https://24a9-147-45-40-23.ngrok-free.app/api/message/webhook/')
        return Response(response)
    else:
        return Response({"User or token not found"}, status=status.HTTP_404_NOT_FOUND)
