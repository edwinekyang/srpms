from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.status import HTTP_200_OK
from rest_framework.mixins import (CreateModelMixin, RetrieveModelMixin, UpdateModelMixin,
                                   DestroyModelMixin, ListModelMixin)
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.settings import api_settings
from rest_framework.decorators import action
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .mixins import NestedGenericViewSet
from . import serializers
from . import models
from . import permissions as app_perms
from accounts.models import SrpmsUser
from .serializer_utils import SubmitSerializer, ApproveSerializer
from .filters import UserFilter

# The default settings is set not list
default_perms: list = api_settings.DEFAULT_PERMISSION_CLASSES


class UserViewSet(ReadOnlyModelViewSet):
    """
    Provides read-only user information, as well as the contract they
    involves (own, supervise, convene).

    TODO: let un-privileged users only sees their own contract
    """
    queryset = SrpmsUser.objects.all()
    serializer_class = serializers.UserContractSerializer

    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['username', 'first_name', 'last_name', 'uni_id']
    filterset_class = UserFilter


class CourseViewSet(ModelViewSet):
    """
    A view the allow users to Create, Read, Update, Delete courses.
    """
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer
    permission_classes = default_perms + [app_perms.AllowSafeMethods |
                                          app_perms.IsSuperuser |
                                          app_perms.IsConvener, ]


class AssessmentTemplateViewSet(ModelViewSet):
    """
    A view the allow users to Create, Read, Update, Delete assessment templates.
    """
    queryset = models.AssessmentTemplate.objects.all()
    serializer_class = serializers.AssessmentTemplateSerializer
    permission_classes = default_perms + [app_perms.AllowSafeMethods |
                                          app_perms.IsSuperuser |
                                          app_perms.IsConvener, ]

    # TODO: forbid update of template name, as its tight to business logic???


class ContractViewSet(ModelViewSet):
    """
    A view the allow users to Create, Read, Update, Delete contracts.
    """
    queryset = models.Contract.objects.all()
    serializer_class = serializers.ContractSerializer
    permission_classes = default_perms + [app_perms.AllowSafeMethods |
                                          app_perms.AllowPOST |
                                          app_perms.IsSuperuser |
                                          app_perms.IsContractOwner, ]

    def perform_create(self, serializer: serializers.ContractSerializer):

        # Set the contract owner to the requester
        serializer.validated_data['owner'] = self.request.user

        return super(ContractViewSet, self).perform_create(serializer)

    # noinspection PyUnusedLocal
    @action(methods=['PUT', 'PATCH'], detail=True, serializer_class=SubmitSerializer,
            permission_classes=default_perms + [app_perms.IsSuperuser |
                                                app_perms.IsContractOwner, ])
    def submit(self, request, pk=None):
        serializer: SubmitSerializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            contract = self.get_object()
            contract.submit_date = serializer.validated_data['submit']
            contract.save()
            return Response(status=HTTP_200_OK)
        else:
            raise ValidationError()

    # noinspection PyUnusedLocal
    @action(methods=['PUT', 'PATCH'], detail=True, serializer_class=ApproveSerializer,
            permission_classes=default_perms + [app_perms.IsSuperuser |
                                                app_perms.IsConvener, ])
    def approve(self, request, pk=None):
        serializer: ApproveSerializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            contract = self.get_object()
            approve_date = serializer.validated_data['approve']
            if approve_date:
                contract.convener = self.request.user
                contract.convener_approval_date = approve_date
            else:
                contract.convener = None
                contract.convener_approval_date = None
            contract.save()
            return Response(status=HTTP_200_OK)
        else:
            raise ValidationError()


class AssessmentExamineViewSet(CreateModelMixin,
                               RetrieveModelMixin,
                               UpdateModelMixin,
                               DestroyModelMixin,
                               ListModelMixin,
                               NestedGenericViewSet):
    queryset = models.AssessmentExamine.objects.all()
    serializer_class = serializers.AssessmentExamineSerializer
    permission_classes = default_perms + [app_perms.AllowSafeMethods |
                                          app_perms.IsSuperuser |
                                          app_perms.IsContractSupervisor, ]

    def perform_create(self, serializer: serializers.AssessmentExamineSerializer):

        self.attach_attributes(serializer)

        # Forbid individual project to have more than one examine for each assessment
        assessment: models.Assessment = serializer.validated_data['assessment']
        if hasattr(assessment.contract, 'individual_project') and \
                len(models.AssessmentExamine.objects.filter(assessment=assessment)) >= 1:
            raise PermissionDenied('Individual project cannot have more than one exmainer for '
                                   'each assessment.')

        return super(AssessmentExamineViewSet, self).perform_create(serializer)

    def perform_update(self, serializer):

        self.attach_attributes(serializer)

        return super(AssessmentExamineViewSet, self).perform_update(serializer)

    # noinspection PyUnusedLocal
    @action(methods=['PUT', 'PATCH'], detail=True, serializer_class=ApproveSerializer,
            permission_classes=default_perms + [app_perms.IsSuperuser |
                                                app_perms.IsConvener |
                                                app_perms.IsContractAssessmentExaminer, ])
    def approve(self, request, pk=None, parent_lookup_contract=None, parent_lookup_assessment=None):
        """Allow examiners to approve assessments"""
        serializer: ApproveSerializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            assessment_examine = self.get_object()
            assessment_examine.examiner_approval_date = serializer.validated_data['approve']
            return Response(status=HTTP_200_OK)
        else:
            raise ValidationError()

    def attach_attributes(self, serializer: serializers.AssessmentExamineSerializer) -> None:
        serializer.validated_data['assessment'] = self.resolved_parents['assessment']
        serializer.validated_data['contract'] = self.resolved_parents['contract']


class AssessmentViewSet(CreateModelMixin,
                        RetrieveModelMixin,
                        UpdateModelMixin,
                        DestroyModelMixin,
                        ListModelMixin,
                        NestedGenericViewSet):
    """
    This ViewSet automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = models.Assessment.objects.all()
    serializer_class = serializers.AssessmentSerializer
    permission_classes = default_perms + [app_perms.AllowSafeMethods |
                                          app_perms.IsSuperuser |
                                          app_perms.IsContractOwner, ]

    def perform_create(self, serializer):
        serializer.validated_data['contract'] = self.resolved_parents['contract']

        # Forbid creation of extra assessments for individual project
        contract = serializer.validated_data['contract']
        if hasattr(contract, 'individual_project'):
            raise PermissionDenied('Cannot create assessments for individual project ')

        return super(AssessmentViewSet, self).perform_create(serializer)

    def perform_update(self, serializer):
        serializer.validated_data['contract'] = self.resolved_parents['contract']

        # Forbid editing assessment template for individual project
        contract = serializer.validated_data['contract']
        if hasattr(contract, 'individual_project') and serializer.validated_data['template']:
            raise PermissionDenied('Cannot edit template for individual project ')

        return super(AssessmentViewSet, self).perform_update(serializer)


class SuperviseViewSet(CreateModelMixin,
                       RetrieveModelMixin,
                       UpdateModelMixin,
                       DestroyModelMixin,
                       ListModelMixin,
                       NestedGenericViewSet):
    """
    This ViewSet automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = models.Supervise.objects.all()
    serializer_class = serializers.SuperviseSerializer
    permission_classes = default_perms + [app_perms.AllowSafeMethods |
                                          app_perms.IsSuperuser |
                                          app_perms.IsContractOwner |
                                          app_perms.IsContractSupervisor, ]

    def perform_create(self, serializer: serializers.SuperviseSerializer):

        self.attach_attributes(serializer)

        # Forbid more than 1 supervisor for individual project
        contract: models.Contract = self.resolved_parents['contract']
        if len(models.Supervise.objects.filter(contract=contract)) >= 1:
            raise PermissionDenied('Individual project does not allowed more than 1 supervisor.')

        self.check_field_permission(serializer)

        return super(SuperviseViewSet, self).perform_create(serializer)

    def perform_update(self, serializer: serializers.SuperviseSerializer):

        self.attach_attributes(serializer)
        self.check_field_permission(serializer)

        return super(SuperviseViewSet, self).perform_update(serializer)

    # noinspection PyUnusedLocal
    @action(methods=['PUT', 'PATCH'], detail=True, serializer_class=ApproveSerializer,
            permission_classes=default_perms + [app_perms.IsSuperuser |
                                                app_perms.IsConvener |
                                                app_perms.IsContractSuperviseOwner, ])
    def approve(self, request, pk=None, parent_lookup_contract=None):
        """Allow supervisor to approve supervise relation"""
        serializer: ApproveSerializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            supervise = self.get_object()
            supervise.supervisor_approval_date = serializer.validated_data['approve']
            return Response(status=HTTP_200_OK)
        else:
            raise ValidationError()

    def attach_attributes(self, serializer: serializers.SuperviseSerializer) -> None:
        """Attach automatic attributes according to the request url and content"""

        serializer.validated_data['contract'] = self.resolved_parents['contract']

        # Check if supervisor is approved, if yes, set the is_formal attribute
        supervisor = serializer.validated_data['supervisor']
        if supervisor.has_perm('research_mgt.can_supervise'):
            serializer.validated_data['is_formal'] = True
        else:
            serializer.validated_data['is_formal'] = False

    def check_field_permission(self, serializer: serializers.SuperviseSerializer) -> None:
        # Forbid normal user to nominate unapproved supervisors
        requester: SrpmsUser = self.request.user
        if app_perms.IsSuperuser.check(requester) or app_perms.IsConvener.check(requester):
            pass
        elif app_perms.IsContractFormalSupervisor.check(self.resolved_parents['contract'],
                                                        requester):
            pass
        elif serializer.validated_data['is_formal']:
            pass
        else:
            raise PermissionDenied('Nominate un-approved supervisor is not allowed')
