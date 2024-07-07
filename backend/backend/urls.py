from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static
from channels.routing import ProtocolTypeRouter, URLRouter
from messaging_app.consumers import MessageConsumer
from messaging_app.views import WebSocketTestView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'),
         name='api-docs'),
    path('api/user/', include('user_app.urls'), name='api-users'),
    path('api/message/', include('messaging_app.urls'), name='api-messaging'),
    path('api/service/', include('services_app.urls'), name='api-services'),
    path('websocket-test/', WebSocketTestView.as_view(), name='websocket_test'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

application = ProtocolTypeRouter({
    'websocket': URLRouter([
        path('ws/messages/', MessageConsumer.as_asgi()),
    ]),
})

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        }
    },
    'INFO': {
        'title': 'Project API',
        'version': '1.0.0',
        'description': 'API for HR Hub project',
    },
}
