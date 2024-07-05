from django.urls import path
from .views import (
    ServiceAccountCreateView, ServiceAccountListView,
    ServiceAccountDeleteView, TelegramServiceAccountListView,
    YandexMailServiceAccountListView, VKServiceAccountListView,
    AvitoRegistrationView
    YandexMailServiceAccountListView,  ServiceAccountUpdateView
)

urlpatterns = [
    path('create/', ServiceAccountCreateView.as_view(),
         name='ServiceAccount_create'),
    path('list/', ServiceAccountListView.as_view(), name='ServiceAccount_list'),
    path('delete/<int:id>/', ServiceAccountDeleteView.as_view(),
         name='ServiceAccount_delete'),
    path('list_tg/', TelegramServiceAccountListView.as_view(),
         name='TelegramServiceAccount_list'),
    path('list_yandex_mail/', YandexMailServiceAccountListView.as_view(),
         name='YandexMailServiceAccount_list'),
    path('list_vk/', VKServiceAccountListView.as_view(),
         name='VKServiceAccount_list'),
    path('avito_registration/', AvitoRegistrationView.as_view(),
         name='Avito_registration')
    path('update/<int:id>/', ServiceAccountUpdateView.as_view(), name='ServiceAccount_update'),
    path('delete/<int:id>/', ServiceAccountDeleteView.as_view(), name='ServiceAccount_delete'),
]
