from rest_framework import viewsets
from rest_framework.settings import api_settings

from . import serializers
from . import models
from . import permissions as app_perms
from accounts.models import SrpmsUser

# The default settings is set not list
default_perms: list = api_settings.DEFAULT_PERMISSION_CLASSES


class CourseViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer
    permission_classes = default_perms + [app_perms.DefaultObjectPermission]


class ContractViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = models.Contract.objects.all()
    serializer_class = serializers.ContractSerializer
    permission_classes = default_perms + [app_perms.DefaultObjectPermission]

    def perform_create(self, serializer: serializers.ContractSerializer):
        """When convener approved, automatically attach the convener to the contract"""
        if hasattr(serializer.validated_data, 'convener_approval_date'):
            serializer.validated_data['convener'] = self.request.user
        serializer.validated_data['owner'] = self.request.user
        super(ContractViewSet, self).perform_create(serializer)

    def perform_update(self, serializer):
        """When convener approved, automatically attach the convener to the contract"""
        if hasattr(serializer.validated_data, 'convener_approval_date'):
            serializer.validated_data['convener'] = self.request.user
        super(ContractViewSet, self).perform_update(serializer)


class AssessmentTemplateViewSet(viewsets.ModelViewSet):
    queryset = models.AssessmentTemplate.objects.all()
    serializer_class = serializers.AssessmentTemplateSerializer
    permission_classes = default_perms + [app_perms.DefaultObjectPermission]


class AssessmentMethodViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = models.AssessmentMethod.objects.all()
    serializer_class = serializers.AssessmentMethodSerializer
    permission_classes = default_perms + [app_perms.DefaultObjectPermission]


class SuperviseViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = models.Supervise.objects.all()
    serializer_class = serializers.SuperviseSerializer
    permission_classes = default_perms + [app_perms.DefaultObjectPermission]

    def perform_create(self, serializer: serializers.SuperviseSerializer):
        """Check if supervisor is approved, if yes, set the is_form attribute"""
        supervisor = SrpmsUser.objects.get(serializer.validated_data['supervisor'])
        if supervisor.has_perm('can_supervise'):
            serializer.validated_data['is_formal'] = True
        super(SuperviseViewSet, self).perform_create(serializer)

    def perform_update(self, serializer: serializers.SuperviseSerializer):
        """Check if supervisor is approved, if yes, set the is_form attribute"""
        supervisor = SrpmsUser.objects.get(serializer.validated_data['supervisor'])
        if supervisor.has_perm('can_supervise'):
            serializer.validated_data['is_formal'] = True
        super(SuperviseViewSet, self).perform_update(serializer)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = SrpmsUser.objects.all()
    serializer_class = serializers.UserContractSerializer
