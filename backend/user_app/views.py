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
        usernames_and_services = request.data.get('usernames_and_services')
        if serializer.is_valid():
            serializer.save()
            custom_user = CustomUser.objects.get(id=serializer.data['id'])
            accounts = ServiceAccount.objects.filter(user_id=request.user.id)
            unique_usernames_and_urls = Message.objects.filter(account__in=accounts).values('account__service_name', 'from_username', 'personal_chat_link').distinct()
            members_of_group_serializer = MembersOfGroupSerializer()
            response_data = serializer.data.copy()
            data = []
            username_service_set = {(item['username'], item['service']) for item in usernames_and_services}
            for item in unique_usernames_and_urls:
                username = item['from_username']
                service = item['account__service_name']

                member_data = {
                    'group': custom_user.id,
                    'user_name_from_message': username,
                    'service_name': service,
                    'chat_link': item['personal_chat_link'],
                    'added': (username, service) in username_service_set
                }

                members_of_group_serializer = MembersOfGroupSerializer(data=member_data)
                if members_of_group_serializer.is_valid():
                    member = members_of_group_serializer.save()
                    data.append(MembersOfGroupSerializer(member).data)
                else:
                    return Response(members_of_group_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            response_data['members'] = data
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Получение всех кастомных пользователей и входящих в них username",
        responses={200: CustomUserSerializer},
        summary="Получение всех кастомных пользователей и входящих в них username",
    )
    def get(self, request, *args, **kwargs):
        custom_users = CustomUser.objects.filter(user=request.user)
        if not custom_users:
            return Response([], status=status.HTTP_200_OK)

        page = self.paginate_queryset(custom_users)
        if page is None:
            page = custom_users

        serializer = self.get_serializer(page, many=True)
        response_data = serializer.data

        for data in response_data:
            members_of_group = MembersOfGroup.objects.filter(group_id=data['id'])
            members_of_group_serializer = MembersOfGroupSerializer(members_of_group, many=True)
            data['members'] = members_of_group_serializer.data

        if self.paginator:
            return self.get_paginated_response(response_data)
        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(tags=['User'])
class ManageCustomUserView(GenericAPIView):
    serializer_class = UserUpdateSchema
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="Добавление и удаление людей, входящих в группу кастомного пользователя, а так же обновление названия группы и профессии."
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
        try:
            custom_user = CustomUser.objects.get(id=group_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Custom user not found'}, status=status.HTTP_404_NOT_FOUND)
        if custom_user.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        if 'group_name' in request.data:
            custom_user.group_name = request.data['group_name']
        if 'profession' in request.data:
            custom_user.profession = request.data['profession']
        custom_user.save()

        members_data = request.data.get('members', {})
        for member_id, is_added in members_data.items():
            if not isinstance(is_added, bool):
                return Response({'error': 'Invalid data for members'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                member = MembersOfGroup.objects.get(id=member_id, group=custom_user)
                member.added = is_added
                member.save()
            except MembersOfGroup.DoesNotExist:
                return Response({'error': f'Member with id {member_id} not found'}, status=status.HTTP_404_NOT_FOUND)
        updated_custom_user = CustomUser.objects.get(id=group_id)
        members_of_custom_user = MembersOfGroup.objects.filter(group=updated_custom_user)
        custom_user_serializer = CustomUserSerializer(updated_custom_user)
        members_serializer = MembersOfGroupSerializer(members_of_custom_user, many=True)
        response_data = custom_user_serializer.data.copy()
        response_data['members'] = members_serializer.data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Добавление и удаление людей, входящих в группу кастомного пользователя, а так же обновление названия группы и профессии."
        "Необходимо передать массив из словарей, которые содержат id пользователей внутри группы. Переданные пользователи будут добавлены в группу, а остальные удалены",
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
        summary="Полное обновление кастомного пользователя",
    )
    def put(self, request, group_id, *args, **kwargs):
        try:
            custom_user = CustomUser.objects.get(id=group_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Custom user not found'}, status=status.HTTP_404_NOT_FOUND)
        if custom_user.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        if 'group_name' in request.data:
            custom_user.group_name = request.data['group_name']
        if 'profession' in request.data:
            custom_user.profession = request.data['profession']
        custom_user.save()

        new_member_ids = set(int(id) for id in request.data.get('members', []))

        existing_members = MembersOfGroup.objects.filter(group=custom_user)
        for member in existing_members:
            member.added = member.id in new_member_ids
            member.save()
        updated_custom_user = CustomUser.objects.get(id=group_id)
        members_of_custom_user = MembersOfGroup.objects.filter(group=updated_custom_user)
        custom_user_serializer = CustomUserSerializer(updated_custom_user)
        members_serializer = MembersOfGroupSerializer(members_of_custom_user, many=True)
        response_data = custom_user_serializer.data.copy()
        response_data['members'] = members_serializer.data
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

    @extend_schema(
        description="Получение членов группы кастомного пользователя",
        responses={200: MembersOfGroupSerializer},
        summary="Получение членов группы кастомного пользователя",
    )
    def get(self, request, group_id, *args, **kwargs):
        custom_user = get_object_or_404(CustomUser, id=group_id)
        if custom_user.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        members_of_custom_user = MembersOfGroup.objects.filter(group=custom_user)
        members_serializer = MembersOfGroupSerializer(members_of_custom_user, many=True)
        response_data = {
            'id': custom_user.id,
            'group_name': custom_user.group_name,
            'profession': custom_user.profession,
            'created_at': custom_user.created_at,
            'members': members_serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(tags=['User'])
class GetUsernamesFromMessages(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="Получение всех возможных username и их сервисов, которые можно объединить в группу",
        responses={200: MembersOfGroupSerializer},
        summary="Получение всех возможных username и их сервисов, которые можно объединить в группу",
    )
    def get(self, request):
        accounts = ServiceAccount.objects.filter(user_id=request.user.id)
        if not accounts:
            return Response([], status=status.HTTP_200_OK)
        unique_usernames = Message.objects.filter(account__in=accounts).values('account__service_name', 'from_username', 'personal_chat_link').distinct()
        data = []
        index = 0
        for items in unique_usernames:
            member_data = {
                'id': index,
                'username_from_message': items['from_username'],
                'service_name': items['account__service_name'],
                'chat_link': items['personal_chat_link'],
            }
            index += 1
            data.append(member_data)
        return Response(data, status=status.HTTP_200_OK)
