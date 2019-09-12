from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'contract', views.ContractViewSet)

course_list = views.CourseList.as_view()

# The API URLs are now determined automatically by the router.
# contract/: List(get) and Create(post)
# contract/pk/: Retrieve(get), Update(post), Partial Update(patch), Destroy(delete)
urlpatterns = format_suffix_patterns([
    path('courses/', course_list, name='course-list'),
    path('', include(router.urls)),
])
