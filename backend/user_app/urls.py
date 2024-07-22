from django.urls import path
from . import views


urlpatterns = [
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.MyTokenRefreshView.as_view(), name='token_refresh'),
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('<int:user_id>/', views.GetUserView.as_view(), name='get_user'),
    path('update-user/', views.ManageUserView.as_view(), name='update'),
    path('custom-user/', views.CustomUserView.as_view(), name='custom_user'),
    path('custom-user/<int:group_id>', views.ManageCustomUserView.as_view(), name='manage_custom_user'),
    path('custom-user/get_uniq_users_from_messages/', views.GetUsernamesFromMessages.as_view(), name='get_uniq_users'),
]
