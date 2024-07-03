from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Message
from .serializers import MessageSerializer, MessageUpdateSerializer
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import DestroyAPIView, UpdateAPIView
from services_app.models import ServiceAccount


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
