from django.urls import path
from django.views.generic import RedirectView

from . import views

# Namespace for this app
app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]