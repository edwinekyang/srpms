"""
URL settings for research_mgt app. Currently related resources are being nested
inside parent resources.

TODO: After reading RESTful API design best practice, it appears that nested resources is
      not a good idea, and would result complicate dependencies. Consider refactor the API
      without nested resources, but use hyperlink for related item.
      https://docs.microsoft.com/en-us/azure/architecture/best-practices/api-design
"""

__author__ = 'Dajie (Cooper) Yang, and Euikyum (Edwin) Yang'
__credits__ = ['Dajie Yang', 'Euikyum Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from django.urls import path, include
from rest_framework import permissions
from rest_framework_extensions.routers import ExtendedDefaultRouter

from .views import (UserViewSet, CourseViewSet, ContractViewSet, AssessmentTemplateViewSet,
                    SuperviseViewSet, AssessmentViewSet, AssessmentExamineViewSet)

app_name = 'research_mgt'

# Router from DRF that automatically generate api root
# '' - 'api-root'
router = ExtendedDefaultRouter()
router.APIRootView.permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Generate the following URL patterns
# 'users/$' - 'user-list'
# 'users/{pk}/$ - 'user-detail'
router.register(r'users', UserViewSet)

# 'course/$' - 'course-list'
# 'course/{pk}/$' - 'course-detail'
router.register(r'courses', CourseViewSet)

# Generate the following URL patterns
# 'assessment-templates/$' - 'assessment-template-list'
# 'assessment-templates/{pk}/$ - 'assessment-template-detail'
router.register(r'assessment-templates',
                AssessmentTemplateViewSet,
                basename='assessment-template')

# Generate the following URL patterns
# 'contracts/$' - 'contract-list'
# 'contracts/{pk}/$ - 'contract-detail'
contract_routes = router.register(r'contracts', ContractViewSet, basename='contract')

# Generate the following URL patterns
# 'contracts/{parent_lookup_contract}/supervise/$' - 'contract-supervise-list'
# 'contracts/{parent_lookup_contract}/supervise/{pk}$ - 'contract-supervise-detail'
contract_routes.register(r'supervise',
                         SuperviseViewSet,
                         basename='contract-supervise',
                         parents_query_lookups=['contract'])

# Generate the following URL patterns
# 'contracts/{parent_lookup_contract}/assessments/$' - 'contract-assessment-list'
# 'contracts/{parent_lookup_contract}/assessments/{pk}$ - 'contract-assessment-detail'
assessment_routes = contract_routes.register(r'assessments',
                                             AssessmentViewSet,
                                             basename='contract-assessment',
                                             parents_query_lookups=['contract'])

# Generate the following URL patterns
# 'contracts/{parent_lookup_contract}/assessments/{parent_lookup_assessment}/$'
# -> 'contract-assessment-examine-list'
# 'contracts/{parent_lookup_contract}/assessments/{parent_lookup_assessment}/examine/{pk}$'
# -> 'contract-assessment-examine-detail'
assessment_routes.register(r'examine',
                           AssessmentExamineViewSet,
                           basename='contract-assessment-examine',
                           parents_query_lookups=['contract', 'assessment'])

urlpatterns = [
    path('', include(router.urls)),
]
