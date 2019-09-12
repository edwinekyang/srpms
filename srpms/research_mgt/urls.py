from django.urls import path
from . import views

# Namespace for this app
app_name = 'research_mgt'

urlpatterns = [
    path('courses/', views.CourseList.as_view(), name='course-list'),
    path('contract/', views.ContractList.as_view(), name='contract-list'),
    path('contract/<int:pk>', views.ContractDetail.as_view(), name='contract-detail')
]
