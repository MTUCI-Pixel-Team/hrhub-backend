from django.urls import path
from messaging_app.consumers import MessageConsumer

websocket_urlpatterns = [
    path('ws/messages/', MessageConsumer.as_asgi()),
]
