from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import ServiceAccount
from .serializers import ServiceAccountSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView


@extend_schema(tags=['ServiceAccount'])
class ServiceAccountCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceAccountSerializer

    def post(self, request, *args, **kwargs):
        allowed_service_names = ['Telegram', 'WhatsApp', 'hh.ru', 'Avito', 'Instagram', 'Facebook', 'vk', 'Viber']
        service_name = request.data.get('service_name')
        if service_name not in allowed_service_names:
            return Response({"detail": f"Invalid service name. Allowed values are {', '.join(allowed_service_names)}."},
                            status=status.HTTP_400_BAD_REQUEST)

        if ServiceAccount.objects.filter(user_id=request.user.id, service_name=service_name).exists():
            return Response({"detail": "A account with this service already exists for the user."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['ServiceAccount'])
class ServiceAccountListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceAccountSerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return ServiceAccount.objects.filter(user_id=user.id)