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

# 'individual/$' - 'individual-list'
# 'individual/{pk}/$' - 'individual-detail'
router.register(r'individual', views.IndividualProjectViewSet)

# 'course/$' - 'course-list'
# 'course/{pk}/$' - 'course-list-detail'
router.register(r'course', views.CourseViewSet)

# 'supervise/$' - 'supervise-list'
router.register(r'supervise', views.SuperviseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
