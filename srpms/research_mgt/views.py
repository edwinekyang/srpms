from rest_framework import viewsets

from .models import Course, IndividualProject, AssessmentMethod, Supervise
from research_mgt.serializers import CourseSerializer, IndividualProjectSerializer, AssessmentMethodSerializer, \
    SuperviseSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    List all courses.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class IndividualProjectViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = IndividualProject.objects.all()
    serializer_class = IndividualProjectSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class AssessmentMethodViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = AssessmentMethod.objects.all()
    serializer_class = AssessmentMethodSerializer


class SuperviseViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Supervise.objects.all()
    serializer_class = SuperviseSerializer
