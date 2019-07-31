from django.urls import path
from django.views.generic import RedirectView

from . import views

# Namespace for this app
app_name = 'accounts'

urlpatterns = [
    path('', RedirectView.as_view(url='login/')),
    path('login/', views.login, name='login'),
]