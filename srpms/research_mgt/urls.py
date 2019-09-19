from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# Namespace for this app
app_name = 'research_mgt'

router = DefaultRouter()
router.register(r'individual', views.IndividualProjectViewSet)
router.register(r'course', views.CourseViewSet)
router.register(r'assessment', views.AssessmentMethodViewSet)
router.register(r'supervise', views.SuperviseViewSet)
'''
urlpatterns = [
    path('courses/', views.CourseList.as_view(), name='course-list'),
    path('contract/', views.ContractList.as_view(), name='contract-list'),
    path('contract/<int:pk>', views.ContractDetail.as_view(), name='contract-detail')
]
'''
urlpatterns = [
    path('', include(router.urls)),
]
