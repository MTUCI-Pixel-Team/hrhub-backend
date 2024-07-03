from django.urls import path
from .views import ServiceAccountCreateView, ServiceAccountListView, ServiceAccountDeleteView

urlpatterns = [
    path('create/', ServiceAccountCreateView.as_view(), name='ServiceAccount_create'),
    path('list/', ServiceAccountListView.as_view(), name='ServiceAccount_list'),
    path('delete/<int:id>/', ServiceAccountDeleteView.as_view(), name='ServiceAccount_delete'),
]
