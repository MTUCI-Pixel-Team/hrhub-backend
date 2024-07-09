from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_message_to_user(user_id, message, service_name):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "send_message",
            "message": message,
            "service_name": service_name
        }
    )
