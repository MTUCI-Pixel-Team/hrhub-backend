from django.urls import path
from . import views

urlpatterns = [
    path('message/create/', views.MessageCreateView.as_view(), name='Message_create'),
    path('message/list/', views.MessageListView.as_view(), name='Message_list'),
    path('message/delete/<int:id>/', views.MessageDeleteView.as_view(), name='Message_delete'),
    path('message/update/<int:id>/', views.MessageUpdateView.as_view(), name='Message_update'),
    path('message/unread/', views.UnreadMessageListView.as_view(), name='Message_unread'),
]
