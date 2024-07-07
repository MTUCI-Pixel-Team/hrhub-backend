from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('create/', views.MessageCreateView.as_view(), name='Message_create'),
    path('list/', views.MessageListView.as_view(), name='Message_list'),
    path('delete/<int:id>/', views.MessageDeleteView.as_view(),
         name='Message_delete'),
    path('update/<int:id>/', views.MessageUpdateView.as_view(),
         name='Message_update'),
    path('unread/', views.UnreadMessageListView.as_view(), name='Message_unread'),
    path('webhook/', csrf_exempt(views.webhook), name='webhook'),
    path('register_webhook/', views.register_webhook, name='register_webhook'),
]
