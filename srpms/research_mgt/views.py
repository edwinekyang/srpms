from rest_framework import viewsets
from rest_framework import permissions

from . import serializers
from . import models
from accounts.models import SrpmsUser


class CourseViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer


class ContractViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = models.Contract.objects.all()
    serializer_class = serializers.ContractSerializer


class AssessmentTemplateViewSet(viewsets.ModelViewSet):
    queryset = models.AssessmentTemplate.objects.all()
    serializer_class = serializers.AssessmentTemplateSerializer


class AssessmentMethodViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = models.AssessmentMethod.objects.all()
    serializer_class = serializers.AssessmentMethodSerializer
    permission_classes = [permissions.IsAuthenticated, ]


class SuperviseViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = models.Supervise.objects.all()
    serializer_class = serializers.SuperviseSerializer
    permission_classes = [permissions.IsAuthenticated, ]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = SrpmsUser.objects.all()
    serializer_class = serializers.UserContractSerializer
    permission_classes = [permissions.IsAuthenticated, ]
