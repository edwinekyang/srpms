from django.urls import path

from . import views

urlpatterns = [
    # ex: /research_mgt/
    path('courses/', views.course_list, name='courses')
]
