import json
from channels.generic.websocket import AsyncWebsocketConsumer


class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("messages", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("messages", self.channel_name)

    # Обработка полученыых сообщений
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Отправка сообщения в веб-сокет
        await self.channel_layer.group_send(
            "messages",
            {
                "type": "chat_message",
                "message": message
            }
        )

    # Отправка сообщения в веб-сокет
    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
