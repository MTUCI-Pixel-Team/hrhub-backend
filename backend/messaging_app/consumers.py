from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
import json
import asyncio


class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user', AnonymousUser())
        if self.user.is_anonymous:
            await self.send(text_data=json.dumps({
                'type': 'сonnection_failed',
                'message': 'You are not authenticated.',
            }))
            await self.close(code=4000)
        else:
            self.group_name = f"user_{self.user.id}"
            try:
                await self.channel_layer.group_add(
                    self.group_name,
                    self.channel_name
                )
                await self.accept()
                self.ping_task = asyncio.create_task(self.ping_client())
                await self.send(text_data=json.dumps({
                    'type': 'connection_established',
                    'message': 'OK',
                    'group': self.group_name,
                }))
            except Exception as e:
                await self.send(text_data=json.dumps({
                    'type': 'сonnection_failed',
                    'message': f'Error during connection: {e}',
                    'group': self.group_name,
                }))
                await self.close(code=1011)

    async def disconnect(self, close_code=1000):
        if hasattr(self, 'group_name') and self.user.is_authenticated:
            self.ping_task.cancel()
            try:
                await self.channel_layer.group_discard(
                    self.group_name,
                    self.channel_name
                )
            except Exception as e:
                await self.send(text_data=json.dumps({
                    'type': 'connection_closed_error',
                    'message': f'Error during connection closing: {e}',
                    'code': close_code
                }))

    async def ping_client(self):
        while True:
            try:
                await self.send(text_data='ping')
                await asyncio.sleep(60)

                if not hasattr(self, 'last_pong') or asyncio.get_event_loop().time() - self.last_pong > 70:
                    await self.close()
                    break
            except Exception as e:
                await self.send(text_data=str(e))
                break

    async def receive(self, text_data=None):
        if text_data == 'pong':
            self.last_pong = asyncio.get_event_loop().time()
            return
        else:
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
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Message is empty.'
                }))

    async def send_message(self, event):
        service_name = event['service_name']
        message = event['message']
        await self.send(text_data=json.dumps({
            'service_name': service_name,
            'message': message
        }))
