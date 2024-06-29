from django.urls import path
from . import views


urlpatterns = [
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.MyTokenRefreshView.as_view(), name='token_refresh'),
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('<int:user_id>/', views.GetUserView.as_view(), name='get_user'),
    path('update-user/', views.ManageUserView.as_view(), name='update'),
]
