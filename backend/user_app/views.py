from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema
from .models import User
from .serializers import UserSerializer, MyTokenObtainPairSerializer
from rest_framework.generics import GenericAPIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response


@extend_schema(tags=['User'])
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(tags=['User'])
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@extend_schema(tags=['User'])
class MyTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(tags=['User'])
class GetUserView(GenericAPIView):
    serializer_class = UserSerializer

    def get(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, id=user_id)
        serializer = self.get_serializer(user)
        data = serializer.data.copy()

        if request.user.id == user.id:
            data['is_owner'] = True
        else:
            data['is_owner'] = False
        return Response(data)


@extend_schema(tags=['User'])
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
