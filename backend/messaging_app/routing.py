from django.urls import re_path
from messaging_app.consumers import MessageConsumer

websocket_urlpatterns = [
    re_path(r'ws/user/(?P<user_id>\d+)/messages/$', MessageConsumer.as_asgi()),
]
