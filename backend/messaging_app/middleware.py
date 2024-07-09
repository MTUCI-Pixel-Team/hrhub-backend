
# import jwt
# from django.conf import settings
# from channels.db import database_sync_to_async
# from django.contrib.auth.models import User
# from urllib.parse import parse_qs
# from channels.middleware import BaseMiddleware

# class JWTAuthMiddleware(BaseMiddleware):

#     @database_sync_to_async
#     def get_user(self, token):
#         try:
#             payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
#             user = User.objects.get(id=payload['user_id'])
#             return user
#         except:
#             return None

#     async def __call__(self, scope, receive, send):
#         query_string = parse_qs(scope['query_string'].decode())
#         token = query_string.get('token')
#         if token:
#             user = await self.get_user(token[0])
#             if user:
#                 scope['user'] = user
#         return await super().__call__(scope, receive, send)
