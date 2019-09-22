from rest_framework import viewsets
from rest_framework.settings import api_settings
from rest_framework.exceptions import PermissionDenied

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
        """
        Mainly perform object/field & method based permission checking, happen after
        permission_class check passed, and data in serializer has been validated
        """

        # When convener approved, automatically attach the convener to the contract
        if bool(serializer.validated_data['convener_approval_date']):
            serializer.validated_data['convener'] = self.request.user

        # Set the owner to the requester
        serializer.validated_data['owner'] = self.request.user

        return super(ContractViewSet, self).perform_create(serializer)

    def perform_update(self, serializer: serializers.ContractSerializer):
        """
        Mainly perform object/field & method based permission checking, happen after
        permission_class check passed, and data in serializer has been validated
        """

        # When convener approved, automatically attach the convener to the contract
        if bool(serializer.validated_data['convener_approval_date']):
            serializer.validated_data['convener'] = self.request.user

        return super(ContractViewSet, self).perform_update(serializer)


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

    def perform_create(self, serializer):
        """
        Mainly perform object/field & method based permission checking, happen after
        permission_class check passed, and data in serializer has been validated
        """

        # Check if the user is allowed to create assessment for a contract
        requester: SrpmsUser = self.request.user
        contract: models.Contract = serializer.validated_data['contract']
        if requester.has_perm('research_mgt.is_mgt_superuser'):
            # Allow superuser
            pass
        elif contract.is_convener_approved():
            raise PermissionDenied("Convener approved contract is read-only")
        elif requester.has_perm('research_mgt.can_convene'):
            # Allow convener
            pass
        elif contract in requester.own.all():
            # Allow contract owner
            pass
        elif contract in requester.supervise.all():
            # Allow supervisors that are involved in this contract
            pass
        else:
            raise PermissionDenied("You're only allowed to create assessment relation if:\n"
                                   "1. This is for your own contract\n"
                                   "2. You're supervising this contract, and you're an "
                                   "approved supervisor")

        return super(AssessmentMethodViewSet, self).perform_create(serializer)


class SuperviseViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = models.Supervise.objects.all()
    serializer_class = serializers.SuperviseSerializer
    permission_classes = default_perms + [app_perms.DefaultObjectPermission]

    def perform_create(self, serializer: serializers.SuperviseSerializer):
        """
        Mainly perform object/field & method based permission checking, happen after
        permission_class check passed, and data in serializer has been validated
        """

        # Check if the user is allowed to create supervise relation
        requester: SrpmsUser = self.request.user
        contract: models.Contract = serializer.validated_data['contract']
        supervisor: SrpmsUser = serializer.validated_data['supervisor']
        if requester.has_perm('research_mgt.is_mgt_superuser'):
            # Allow superuser
            pass
        elif contract.is_convener_approved():
            raise PermissionDenied("Convener approved contract is read-only")
        elif requester.has_perm('research_mgt.can_convene'):
            # Allow convener
            pass
        elif contract in requester.own.all() \
                and supervisor.has_perm('research_mgt.approved_supervisors'):
            # Allow contract owner to nominate approved supervisors
            pass
        elif requester.has_perm('research_mgt.approved_supervisors') \
                and contract in requester.supervise.all():
            # Allow approved supervisors that are involved in this contract
            pass
        else:
            raise PermissionDenied("You're only allowed to create supervise relation if:\n"
                                   "1. This is your contract, and you are nominating an "
                                   "approved supervisor\n"
                                   "2. You're supervising this contract, and you're an "
                                   "approved supervisor")

        # Check if supervisor is an approved supervisor, if yes, set the is_form attribute
        supervisor = serializer.validated_data['supervisor']
        if supervisor.has_perm('can_supervise'):
            serializer.validated_data['is_formal'] = True
        else:
            serializer.validated_data['is_formal'] = False

        return super(SuperviseViewSet, self).perform_create(serializer)

    def perform_update(self, serializer: serializers.SuperviseSerializer):
        """
        Mainly perform object/field & method based permission checking, happen after
        permission_class check passed, and data in serializer has been validated
        """

        # Check if supervisor is approved, if yes, set the is_form attribute
        supervisor = serializer.validated_data['supervisor']
        if supervisor.has_perm('can_supervise'):
            serializer.validated_data['is_formal'] = True
        else:
            serializer.validated_data['is_formal'] = False

        return super(SuperviseViewSet, self).perform_update(serializer)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = SrpmsUser.objects.all()
    serializer_class = serializers.UserContractSerializer
