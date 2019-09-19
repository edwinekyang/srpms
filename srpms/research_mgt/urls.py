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
# 'assessment-methods/$' - 'assessment-method-list'
# 'assessment-methods/{pk}/$ - 'assessment-method-detail'
router.register(r'assessment-methods', views.AssessmentMethodViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # ex: /research_mgt/5/detail/
    path('<int:contract_id>/detail/', views.detail, name='detail'),
    # ex: /polls/5/result/
    path('<int:contract_id>/result/', views.result, name='result'),
]
