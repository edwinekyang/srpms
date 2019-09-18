from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from srpms import settings
from . import views

# Namespace for this app
app_name = 'accounts'

urlpatterns = [
    path('', views.APIRootView.as_view(), name='root'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/', views.UserListView.as_view(), name='user-list')
]

if settings.DEBUG:
    urlpatterns += [path('login/', views.LoginView.as_view(), name='login'),
                    path('logout/', views.LogoutView.as_view(), name='logout'), ]
