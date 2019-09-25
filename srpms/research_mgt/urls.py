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
# 'contracts/{parents_query_lookups}/supervise/$' - 'contract-supervise-list'
# 'contracts/{parents_query_lookups}/supervise/{pk}$ - 'contract-supervise-detail'
contract_routes.register(r'supervise',
                         views.SuperviseViewSet,
                         basename='contract-supervise',
                         parents_query_lookups=['contract'])

# Generate the following URL patterns
# 'contracts/{parents_query_lookups}/assessment-methods/$' - 'contract-assessment-method-list'
# 'contracts/{parents_query_lookups}/assessment-methods/{pk}$ - 'contract-assessment-method-detail'
assessment_routes = contract_routes.register(r'assessment-methods',
                                             views.AssessmentMethodViewSet,
                                             basename='contract-assessment-method',
                                             parents_query_lookups=['contract'])

# Generate the following URL patterns
# 'contracts/{parents_query_lookups[0]}/assessment-methods/{parents_query_lookups[1]}/$'
# -> 'contract-assessment-method-examine-list'
# 'contracts/{parents_query_lookups[0]}/assessment-methods/{parents_query_lookups[1]}/examine/{pk}$'
# -> 'contract-assessment-method-examine-detail'
assessment_routes.register(r'examine',
                           views.AssessmentExamineViewSet,
                           basename='contract-assessment-method-examine',
                           parents_query_lookups=['contract', 'assessment'])

urlpatterns = [
    path('', include(router.urls)),
]
