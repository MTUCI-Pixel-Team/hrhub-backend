from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Message
from .serializers import MessageSerializer, MessageUpdateSerializer
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import DestroyAPIView, UpdateAPIView


@extend_schema(tags=['Message'])
class MessageCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
