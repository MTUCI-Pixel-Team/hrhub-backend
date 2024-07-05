from django.urls import path
from .views import (
    ServiceAccountCreateView, ServiceAccountListView,
    ServiceAccountDeleteView, TelegramServiceAccountListView,
    YandexMailServiceAccountListView,  ServiceAccountUpdateView
)

urlpatterns = [
    path('create/', ServiceAccountCreateView.as_view(), name='ServiceAccount_create'),
    path('list/', ServiceAccountListView.as_view(), name='ServiceAccount_list'),
    path('update/<int:id>/', ServiceAccountUpdateView.as_view(), name='ServiceAccount_update'),
    path('delete/<int:id>/', ServiceAccountDeleteView.as_view(), name='ServiceAccount_delete'),
    path('list_tg/', TelegramServiceAccountListView.as_view(), name='TelegramServiceAccount_list'),
    path('list_yandex_mail/', YandexMailServiceAccountListView.as_view(), name='YandexMailServiceAccount_list'),
]
