from django.urls import path, include
from rest_framework import permissions
from rest_framework_extensions.routers import ExtendedDefaultRouter

from . import views

app_name = 'research_mgt'

# Router from DRF that automatically generate api root
# '' - 'api-root'
router = ExtendedDefaultRouter()
router.APIRootView.permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Generate the following URL patterns
# 'users/$' - 'user-list'
# 'users/{pk}/$ - 'user-detail'
router.register(r'users', views.UserViewSet)

# 'course/$' - 'course-list'
# 'course/{pk}/$' - 'course-list-detail'
router.register(r'courses', views.CourseViewSet)

# Generate the following URL patterns
# 'assessment-templates/$' - 'assessment-template-list'
# 'assessment-templates/{pk}/$ - 'assessment-template-detail'
router.register(r'assessment-templates', views.AssessmentTemplateViewSet)

# Generate the following URL patterns
# 'contracts/$' - 'contract-list'
# 'contracts/{pk}/$ - 'contract-detail'
contract_routes = router.register(r'contracts', views.ContractViewSet, basename='contract')

# Generate the following URL patterns
# 'contracts/{parents_query_lookups}/supervisors/$' - 'contract-supervisor-list'
# 'contracts/{parents_query_lookups}/supervisors/{pk}$ - 'contract-supervisor-detail'
contract_routes.register(r'supervisors',
                         views.SuperviseViewSet,
                         basename='contract-supervisor',
                         parents_query_lookups=['contract'])

# Generate the following URL patterns
# 'contracts/{parents_query_lookups}/assessment-methods/$' - 'contract-assessment-method-list'
# 'contracts/{parents_query_lookups}/assessment-methods/{pk}$ - 'contract-assessment-method-detail'
contract_routes.register(r'assessment-methods',
                         views.AssessmentMethodViewSet,
                         basename='contract-assessment-method',
                         parents_query_lookups=['contract'])

urlpatterns = [
    path('', include(router.urls)),
]
