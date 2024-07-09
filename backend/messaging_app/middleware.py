from django.conf import settings
from channels.db import database_sync_to_async
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from jwt import decode as jwt_decode, InvalidTokenError
from django.contrib.auth import get_user_model


class JWTAuthMiddleware(BaseMiddleware):
    @database_sync_to_async
    def get_user(self, token):
        User = get_user_model()
        try:
            decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_data['user_id']
            return User.objects.get(id=user_id)
        except (InvalidTokenError, User.DoesNotExist):
            return None

    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope['query_string'].decode())
        token = query_string.get('token')
        if token:
            user = await self.get_user(token[0])
            if user:
                scope['user'] = user
        return await super().__call__(scope, receive, send)
