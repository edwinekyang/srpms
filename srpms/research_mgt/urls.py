from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    # ex: /research_mgt/
    path('courses/', views.CourseList.as_view(), name='courses'),
    path('contract/', views.ContractList.as_view(), name='contract'),
    path('contract/<int:pk>', views.ContractDetail.as_view(), name='contract detail')
]

urlpatterns = format_suffix_patterns(urlpatterns)
