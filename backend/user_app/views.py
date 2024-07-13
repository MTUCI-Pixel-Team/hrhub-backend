from rest_framework import generics, permissions, status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from .models import User, CustomUser, MembersOfGroup
from .serializers import UserSerializer, MyTokenObtainPairSerializer, CustomUserSerializer, MembersOfGroupSerializer
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
        })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
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
        return Response(response_data, status=200)


@extend_schema(tags=['User'])
class ManageCustomUserView(GenericAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="Обновление кастомного пользователя",
        parameters=[
            OpenApiParameter(name='group_id', type=int, location=OpenApiParameter.PATH, description="ID группы для обновления")
        ],
        request=CustomUserSerializer,
        responses={
            status.HTTP_200_OK: CustomUserSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Неверные данные"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Нет прав для выполнения операции"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Кастомный пользователь не найден")
        },
        summary="Обновление кастомного пользователя",
    )
    def patch(self, request, group_id, *args, **kwargs):
        custom_user = CustomUser.objects.get(user=request.user, id=group_id)
        if not custom_user:
            return Response({'error': 'Custom user not found'}, status=404)
        serializer = self.get_serializer(data=request.data, instance=custom_user)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors)

    @extend_schema(
        description="Удаление кастомного пользователя",
        parameters=[
            OpenApiParameter(name='group_id', type=int, location=OpenApiParameter.PATH, description="ID группы для удаления")
        ],
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Кастомный пользователь успешно удален"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Кастомный пользователь не найден"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Нет прав для выполнения операции"),
        },
        summary="Удаление кастомного пользователя",
    )
    def delete(self, request, group_id, *args, **kwargs):
        custom_user = CustomUser.objects.get(user=request.user, id=group_id)
        if not custom_user:
            return Response({'error': 'Custom user not found'}, status=404)
        custom_user.delete()
        return Response({'success': 'Custom user deleted'}, status=200)

    @extend_schema(
        description="Добавление username в группу кастомного пользователя",
        request={"id": "int", "user_name_from_message": "str"},
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(description="Пользователь успешно добавлен в группу"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Неверные данные"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Нет прав для выполнения операции"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Группа или пользователь не найдены"),
        },
        summary="Добавление username в группу кастомного пользователя",
    )
    def post(self, request, group_id, *args, **kwargs):
        custom_user = CustomUser.objects.get(user=request.user.id, id=group_id)
        if not custom_user:
            return Response({'error': 'Custom user not found'}, status=404)
        serializer = MembersOfGroupSerializer(data={
            'group': custom_user.id,
            'user_name_from_message': request.data.get('user_name_from_message'),
        })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['User'])
class ManageCustomUserGroupView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MembersOfGroupSerializer

    @extend_schema(
        description="Удаление пользователя из группы кастомного пользователя",
        parameters=[
            OpenApiParameter(name='group_id', type=int, location=OpenApiParameter.PATH, description="ID группы кастомного пользователя"),
            OpenApiParameter(name='member_id', type=int, location=OpenApiParameter.PATH, description="ID члена группы для удаления"),
        ],
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Пользователь успешно удален из группы"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Группа или пользователь не найдены"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Нет прав для выполнения операции"),
        },
        summary="Удаление пользователя из группы",
    )
    def delete(self, request, group_id, member_id, *args, **kwargs):
        custom_user = get_object_or_404(CustomUser, id=group_id, user=request.user)
        member = get_object_or_404(MembersOfGroup, id=member_id, group=custom_user)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        description="Обновление информации о пользователе в группе кастомного пользователя",
        parameters=[
            OpenApiParameter(name='group_id', type=int, location=OpenApiParameter.PATH, description="ID группы кастомного пользователя"),
            OpenApiParameter(name='member_id', type=int, location=OpenApiParameter.PATH, description="ID члена группы для обновления"),
        ],
        request=MembersOfGroupSerializer,
        responses={
            status.HTTP_200_OK: MembersOfGroupSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Неверные данные"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Группа или пользователь не найдены"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Нет прав для выполнения операции"),
        },
        summary="Обновление информации о пользователе в группе",
    )
    def put(self, request, group_id, member_id, *args, **kwargs):
        custom_user = get_object_or_404(CustomUser, id=group_id, user=request.user)
        member = get_object_or_404(MembersOfGroup, id=member_id, group=custom_user)

        serializer = self.get_serializer(member, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
