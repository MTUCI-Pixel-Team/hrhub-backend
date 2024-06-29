from django.urls import path
from . import views

urlpatterns = [
    path('message/create/', views.MessageCreateView.as_view(), name='Message_create'),
    path('message/list/', views.MessageListView.as_view(), name='Message_list'),
]
