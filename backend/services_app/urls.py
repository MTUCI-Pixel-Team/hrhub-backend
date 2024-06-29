from django.urls import path
from . import views

urlpatterns = [
    path('serviceaccount/create/', views.ServiceAccountCreateView.as_view(), name='ServiceAccount_create'),
    path('serviceaccount/list/', views.ServiceAccountListView.as_view(), name='ServiceAccount_list'),
    path('serviceaccount/delete/<int:id>/', views.ServiceAccountDeleteView.as_view(), name='ServiceAccount_delete'),
]