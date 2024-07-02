from django.urls import path
from .views import ServiceAccountCreateView, ServiceAccountListView, ServiceAccountDeleteView

urlpatterns = [
    path('serviceaccount/create/', ServiceAccountCreateView.as_view(), name='ServiceAccount_create'),
    path('serviceaccount/list/', ServiceAccountListView.as_view(), name='ServiceAccount_list'),
    path('serviceaccount/delete/<int:id>/', ServiceAccountDeleteView.as_view(), name='ServiceAccount_delete'),
]
