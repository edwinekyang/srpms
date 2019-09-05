from django.urls import path

from . import views

# Namespace for this app
app_name = 'accounts'

urlpatterns = [
    path('user/<str:username>/', views.UserDetailView.as_view(), name='user-detail'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
