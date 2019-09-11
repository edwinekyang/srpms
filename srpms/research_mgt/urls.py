from django.urls import path

from . import views

urlpatterns = [
    # ex: /research_mgt/
    path('', views.contract, name='contract'),
    # ex: /research_mgt/5/detail/
    path('<int:contract_id>/detail/', views.detail, name='detail'),
    # ex: /polls/5/result/
    path('<int:contract_id>/result/', views.result, name='result'),
]