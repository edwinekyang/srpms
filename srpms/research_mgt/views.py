from rest_framework import viewsets
from rest_framework import permissions

from . import serializers
from . import models
from accounts.models import SrpmsUser


class ContractViewSet(viewsets.ModelViewSet):
    queryset = models.Contract.objects.all()
    serializer_class = serializers.ContractSerializer


class SuperviseViewSet(viewsets.ModelViewSet):
    queryset = models.Supervise.objects.all()
    serializer_class = serializers.SuperviseSerializer


class AssessmentTemplateViewSet(viewsets.ModelViewSet):
    queryset = models.AssessmentTemplate.objects.all()
    serializer_class = serializers.AssessmentTemplateSerializer


class AssessmentMethodViewSet(viewsets.ModelViewSet):
    queryset = models.AssessmentMethod.objects.all()
    serializer_class = serializers.AssessmentMethodSerializer
    permission_classes = [permissions.IsAuthenticated, ]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = SrpmsUser.objects.all()
    serializer_class = serializers.UserContractSerializer
    permission_classes = [permissions.IsAuthenticated, ]
