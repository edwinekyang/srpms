from rest_framework import viewsets
from rest_framework import permissions
from django.shortcuts import render
from django.http import HttpResponse

from .forms import ContractForm
from .serializers import UserContractSerializer, CourseSerializer, IndividualProjectSerializer, AssessmentMethodSerializer, \
    SuperviseSerializer
from .models import Course, IndividualProject, AssessmentMethod, Supervise
from accounts.models import SrpmsUser


class CourseViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
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
    permission_classes = [permissions.IsAuthenticated, ]


class SuperviseViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Supervise.objects.all()
    serializer_class = SuperviseSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = SrpmsUser.objects.all()
    serializer_class = UserContractSerializer
    permission_classes = [permissions.IsAuthenticated, ]
