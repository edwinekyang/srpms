from rest_framework import viewsets
from rest_framework.settings import api_settings
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action

from . import serializers
from . import models
from . import permissions as app_perms
from accounts.models import SrpmsUser

# The default settings is set not list
default_perms: list = api_settings.DEFAULT_PERMISSION_CLASSES


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides read-only user information, as well as the contract they
    involves (own, supervise, convene).
    """
    queryset = SrpmsUser.objects.all()
    serializer_class = serializers.UserContractSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    A view the allow users to Create, Read, Update, Delete courses.
    """
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer

    def get_permissions(self):
        permission_class = default_perms
        if self.request.method == 'GET':
            pass
        else:
            permission_class += [app_perms.IsSuperuser | app_perms.IsConvener, ]

        # Below line is from super method
        return [permission() for permission in default_perms]


class AssessmentTemplateViewSet(viewsets.ModelViewSet):
    """
    A view the allow users to Create, Read, Update, Delete assessment templates.
    """
    queryset = models.AssessmentTemplate.objects.all()
    serializer_class = serializers.AssessmentTemplateSerializer

    def get_permissions(self):
        permission_class = default_perms
        if self.request.method == 'GET':
            pass
        else:
            permission_class += [app_perms.IsSuperuser | app_perms.IsConvener, ]

        # Below line is from super method
        return [permission() for permission in default_perms]


class ContractViewSet(viewsets.ModelViewSet):
    """
    A view the allow users to Create, Read, Update, Delete contracts.
    """
    queryset = models.Contract.objects.all()
    serializer_class = serializers.ContractSerializer
    permission_classes = default_perms + [app_perms.DefaultObjectPermission]

    def perform_create(self, serializer: serializers.ContractSerializer):
        """
        Mainly perform object/field & method based permission checking, happen after
        permission_class check passed, and data in serializer has been validated
        """

        # TODO: field level permission

        # When convener approved, automatically attach the convener to the contract
        if serializer.validated_data.get('convener_approval_date', False):
            serializer.validated_data['convener'] = self.request.user

        # Set the owner to the requester
        serializer.validated_data['owner'] = self.request.user

        return super(ContractViewSet, self).perform_create(serializer)

    def perform_update(self, serializer: serializers.ContractSerializer):
        """
        Mainly perform object/field & method based permission checking, happen after
        permission_class check passed, and data in serializer has been validated
        """

        # TODO: field level permission

        # When convener approved, automatically attach the convener to the contract
        if serializer.validated_data.get('convener_approval_date', False):
            serializer.validated_data['convener'] = self.request.user

        return super(ContractViewSet, self).perform_update(serializer)

    @action(methods=['PUT', 'PATCH'], detail=True,
            permission_classes=default_perms + [app_perms.IsSuperuser | app_perms.IsContractOwner])
    def submit(self, request, pk=None):
        # TODO: allow convener to approve contract that aren't approved
        pass

    @action(methods=['PUT', 'PATCH'], detail=True,
            permission_classes=default_perms + [app_perms.IsSuperuser | app_perms.IsConvener, ])
    def convener_approve(self, request, pk=None):
        # TODO: allow convener to approve contract that aren't approved
        pass


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

        # TODO: field level permission

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

    def perform_update(self, serializer):

        # TODO: field level permission

        super(AssessmentMethodViewSet, self).perform_update(serializer)


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
                and contract.supervisor.all() & requester.supervise.all():
            # Allow approved supervisors that are involved in this contract
            pass
        else:
            raise PermissionDenied("You're only allowed to create supervise relation if:\n"
                                   "1. This is your contract, and you are nominating an "
                                   "approved supervisor\n"
                                   "2. You're supervising this contract, and you're an "
                                   "approved supervisor")

        # TODO: field level permission

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

        # TODO: field level permission

        # Check if supervisor is approved, if yes, set the is_formal attribute
        supervisor = serializer.validated_data['supervisor']
        if supervisor.has_perm('can_supervise'):
            serializer.validated_data['is_formal'] = True
        else:
            serializer.validated_data['is_formal'] = False

        return super(SuperviseViewSet, self).perform_update(serializer)
