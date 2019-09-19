from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'research_mgt'

# Router from DRF that automatically generate api root
# '' - 'api-root'
router = DefaultRouter()

# Generate the following URL patterns
# 'users/$' - 'user-list'
# 'users/{pk}/$ - 'user-detail'
router.register(r'users', views.UserViewSet)

# Generate the following URL patterns
# 'assessment-templates/$' - 'assessment-template-list'
# 'assessment-templates/{pk}/$ - 'assessment-template-detail'
router.register(r'assessment-templates', views.AssessmentTemplateViewSet)

# Generate the following URL patterns
# 'assessment-methods/$' - 'assessment-method-list'
# 'assessment-methods/{pk}/$ - 'assessment-method-detail'
router.register(r'assessment-methods', views.AssessmentMethodViewSet)

# Generate the following URL patterns
# 'contracts/$' - 'contract-list'
# 'contracts/{pk}/$ - 'contract-detail'
router.register(r'contracts', views.ContractViewSet)

# Generate the following URL patterns
# 'supervise/$' - 'supervise-list'
# 'supervise/{pk}/$ - 'supervise-detail'
router.register(r'supervise', views.SuperviseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
