from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from jwt import decode as jwt_decode, InvalidTokenError
from django.conf import settings
import json


class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = parse_qs(self.scope['query_string'].decode())
        token = query_string.get('token', [None])[0]

        if token:
            self.user = await self.get_user(token)
        else:
            self.user = AnonymousUser()

        if self.user.is_anonymous:
            print('User not found')
            await self.close()
        else:
            self.group_name = f"user_{self.user.id}"
            print(f"Group name: {self.group_name}")
            try:
                await self.channel_layer.group_add(
                    self.group_name,
                    self.channel_name
                )
                await self.accept()

                await self.send(text_data=json.dumps({
                    'type': 'connection_established',
                    'message': 'OK',
                    'group': self.group_name
                }))
            except Exception as e:
                print(f"Error during connect: {e}")
                await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name') and self.user.is_authenticated:
            try:
                await self.channel_layer.group_discard(
                    self.group_name,
                    self.channel_name
                )
            except Exception as e:
                print(f"Error during disconnect: {e}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        if message is not None:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': data['message']
                }
            )
        else:
            print("Received data does not contain a 'message' key.")

    async def send_message(self, event):
        message_type = event['type']
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': message_type,
            'message': message
        }))

    async def avito_send_message(self, event):
        message_type = event['type']
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': message_type,
            'message': message
        }))

    async def vk_send_message(self, event):
        message_type = event['type']
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': message_type,
            'message': message
        }))

    @database_sync_to_async
    def get_user(self, token):
        User = get_user_model()
        try:
            decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_data['user_id']
            return User.objects.get(id=user_id)
        except (InvalidTokenError, User.DoesNotExist):
            return AnonymousUser()
