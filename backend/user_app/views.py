from rest_framework import generics, permissions, status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from .models import User, CustomUser, MembersOfGroup
from messaging_app.models import Message
from services_app.models import ServiceAccount
from .serializers import UserSerializer, MyTokenObtainPairSerializer, CustomUserSerializer, MembersOfGroupSerializer, UserUpdateSchema
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


@extend_schema(tags=['User'])
class CustomUserView(GenericAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="Создание кастомного пользователя, который может объеденять несколько userneme в одну группу",
        responses={200: CustomUserSerializer},
        summary="Создание кастомного пользователя",
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={
            'user': request.user.id,
            'group_name': request.data.get('group_name'),
            'profession': request.data.get('profession'),
        })
        if serializer.is_valid():
            serializer.save()
            custom_user = CustomUser.objects.get(id=serializer.data['id'])

            accounts = ServiceAccount.objects.filter(user_id=request.user.id)
            unique_usernames_and_urls = Message.objects.filter(account__in=accounts).values('account__service_name', 'from_username', 'personal_chat_link').distinct()
            members_of_group_serializer = MembersOfGroupSerializer()
            response_data = serializer.data.copy()
            data = []
            for items in unique_usernames_and_urls:
                member_data = {
                    'group': custom_user.id,
                    'user_name_from_message': items['from_username'],
                    'service_name': items['account__service_name'],
                    'chat_link': items['personal_chat_link'],
                }
                members_of_group_serializer = MembersOfGroupSerializer(data=member_data)
                if members_of_group_serializer.is_valid():
                    member = members_of_group_serializer.save()
                    data.append(MembersOfGroupSerializer(member).data)
                else:
                    return Response(members_of_group_serializer.errors, status=400)
            response_data['members'] = data
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=400)

    @extend_schema(
        description="Получение всех кастомных пользователей и входящих в них username",
        responses={200: CustomUserSerializer},
        summary="Получение всех кастомных пользователей и входящих в них username",
    )
    def get(self, request, *args, **kwargs):
        custom_users = CustomUser.objects.filter(user=request.user)
        if not custom_users:
            return Response([], status=200)
        response_data = []
        for user in custom_users:
            serializer = self.get_serializer(user)
            data = serializer.data.copy()
            members_of_group = MembersOfGroup.objects.filter(group=user)
            members_of_group_serializer = MembersOfGroupSerializer(members_of_group, many=True)
            data['members'] = members_of_group_serializer.data
            response_data.append(data)
        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(tags=['User'])
class ManageCustomUserView(GenericAPIView):
    serializer_class = UserUpdateSchema
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="Добавление и удаление людей, входящих в группу кастомного пользователя."
        "Необходимо передать массив из словарей, которые содержат id пользователей внутри группы и флаги true/false",
        parameters=[
            OpenApiParameter(name='group_id', type=int, location=OpenApiParameter.PATH, description="ID группы для обновления")
        ],
        request=UserUpdateSchema,
        responses={
            status.HTTP_200_OK: MembersOfGroupSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Неверные данные"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Нет прав для выполнения операции"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Кастомный пользователь не найден")
        },
        summary="Обновление кастомного пользователя",
    )
    def patch(self, request, group_id, *args, **kwargs):
        custom_user = CustomUser.objects.get(id=group_id)
        if not custom_user:
            return Response({'error': 'Custom user not found'}, status=status.HTTP_404_NOT_FOUND)
        if custom_user.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        response_data = []
        for key, value in request.data.items():
            if key.isdigit() and value in [True, False]:
                try:
                    member = MembersOfGroup.objects.get(id=key, group=custom_user)
                    member.added = value
                    member.save()
                    response_data.append(MembersOfGroupSerializer(member).data)
                except MembersOfGroup.DoesNotExist:
                    return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Удаление кастомного пользователя",
        parameters=[
            OpenApiParameter(name='group_id', type=int, location=OpenApiParameter.PATH, description="ID группы для удаления")
        ],
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Участники удалены"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Нет прав для выполнения операции"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Кастомный пользователь не найден")
        },
        summary="Удаление кастомного пользователя",
    )
    def delete(self, request, group_id, *args, **kwargs):
        custom_user = CustomUser.objects.get(id=group_id)
        if not custom_user:
            return Response({'error': 'Custom user not found'}, status=status.HTTP_404_NOT_FOUND)
        if custom_user.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        custom_user.delete()
        return Response({'message': 'Members deleted'}, status=status.HTTP_204_NO_CONTENT)
