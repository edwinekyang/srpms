"""
views.py defines API views for the backend, it contain business logic that are request user
related. Unless otherwise specified, or related to view's @action, request user irrelevant
login should resides in py
"""

__author__ = 'Dajie (Cooper) Yang, and Euikyum (Edwin) Yang'
__credits__ = ['Dajie Yang', 'Euikyum Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = "dajie.yang@anu.edu.au"

from io import BytesIO, StringIO
from typing import List
from django.http import HttpResponse
from django.db import transaction
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.mixins import (CreateModelMixin, RetrieveModelMixin, UpdateModelMixin,
                                   DestroyModelMixin, ListModelMixin)
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.settings import api_settings
from rest_framework.decorators import action
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from accounts.models import SrpmsUser
from .mixins import NestedGenericViewSet
from .serializers import (CourseSerializer, AssessmentTemplateSerializer, UserContractSerializer,
                          ContractSerializer, SuperviseSerializer,
                          AssessmentSerializer, AssessmentExamineSerializer)
from .models import (Course, AssessmentTemplate, Contract, Supervise, Assessment,
                     AssessmentExamine, ActivityLog)
from .permissions import (AllowSafeMethods, AllowPOST,
                          IsConvener, IsSuperuser, IsContractOwner,
                          IsContractSupervisor, IsContractFormalSupervisor,
                          IsContractSuperviseOwner,
                          IsContractAssessmentExaminer, IsExaminerNominator,
                          ContractSubmitted, ContractNotSubmitted,
                          ContractNotApprovedBySupervisor, ContractApprovedBySupervisor,
                          ContractNotFinalApproved, ContractFinalApproved)
from .print import print_individual_project_contract
from .serializer_utils import SubmitSerializer, ApproveSerializer
from .filters import UserFilter
from .signals import (CONTRACT_SUBMIT, CONTRACT_APPROVE, SUPERVISE_APPROVE, EXAMINER_APPROVE,
                      ACTION_CONTRACT_SUBMIT, ACTION_CONTRACT_UN_SUBMIT,
                      ACTION_CONTRACT_APPROVE, ACTION_CONTRACT_DISAPPROVE,
                      ACTION_SUPERVISE_APPROVE, ACTION_SUPERVISE_DISAPPROVE,
                      ACTION_EXAMINER_APPROVE, ACTION_EXAMINER_DISAPPROVE)

# The default settings is set not list
default_perms: list = api_settings.DEFAULT_PERMISSION_CLASSES


class UserViewSet(ReadOnlyModelViewSet):
    """
    Provides read-only user information, as well as the contract they
    involves (own, supervise, examine, convene).
    """

    queryset = SrpmsUser.objects.all()
    serializer_class = UserContractSerializer

    # Support user search and filter 'can_supervise' users
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['username', 'first_name', 'last_name', 'uni_id']
    filterset_class = UserFilter


class CourseViewSet(ModelViewSet):
    """
    A view the allow users to Create, Retrieve, Update, Delete courses.
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = default_perms + [AllowSafeMethods | IsSuperuser | IsConvener, ]


class AssessmentTemplateViewSet(ModelViewSet):
    """
    A view the allow users to Create, Retrieve, Update, Delete assessment templates.
    """

    queryset = AssessmentTemplate.objects.all()
    serializer_class = AssessmentTemplateSerializer
    permission_classes = default_perms + [AllowSafeMethods | IsSuperuser | IsConvener, ]


class ContractViewSet(ModelViewSet):
    """
    A view the allow users to Create, Retrieve, Update, Delete contracts. Also have submit and
    approve action to support contract administration.

    Please note that the API current have two nested serializer, 'individual_project' and
    'special_topic', and only one of them is allowed, the other one should be removed or
    set to null in JSON data for POST, PUT, or PATCH methods.
    """
    serializer_class = ContractSerializer
    permission_classes = default_perms + [AllowSafeMethods | AllowPOST | IsSuperuser |
                                          (IsContractOwner & ContractNotFinalApproved &
                                           ContractNotSubmitted), ]
    filterset_fields = ('year', 'semester', 'course')

    def get_queryset(self) -> QuerySet:
        """
        Override the default method to only allow user retrieve related contracts.
        """

        requester: SrpmsUser = self.request.user

        if IsSuperuser.check(requester):
            # Superuser sees all contract
            self.queryset = Contract.objects.all()
        elif IsConvener.check(requester):
            # Convener sees all contracts that has been submitted at least once.
            self.queryset = Contract.objects.filter(was_submitted=True)
        else:
            # For other users, only display contract that they own, supervise, or examine, or other
            # user's contracts that has passed convener approval.
            # NOTE: supervise and examine would include contracts that have been submitted at least
            #       once
            contract_finalized = Contract.objects.filter(convener_approval_date__isnull=False)
            contract_own = requester.own.all()
            contract_supervise = Contract.objects.filter(
                    supervise__in=requester.supervise.all(), was_submitted=True)
            contract_examine = Contract.objects.filter(
                    assessment_examine__examine__examiner=requester, was_submitted=True)

            queryset = contract_finalized | contract_own | contract_supervise | contract_examine
            self.queryset = queryset.distinct()

        return super(ContractViewSet, self).get_queryset()

    def perform_create(self, serializer: ContractSerializer):
        """Override the default method to automatically attach request user as contract owner"""

        # Set the contract owner to the requester
        serializer.validated_data['owner'] = self.request.user

        return super(ContractViewSet, self).perform_create(serializer)

    # noinspection PyUnusedLocal
    @action(methods=['PUT', 'PATCH'], detail=True, serializer_class=SubmitSerializer,
            permission_classes=default_perms + [IsSuperuser | (IsContractOwner &
                                                               ContractNotSubmitted), ])
    def submit(self, request, pk=None):
        """The submit action for contract owner to submit their contract."""

        serializer: SubmitSerializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            contract = self.get_object()
            contract.submit_date = serializer.validated_data['submit']
            contract.was_submitted = True
            contract.save()

            # Log activity, and send signal to trigger notifications
            activity_log = ActivityLog.objects.create(actor=self.request.user,
                                                      action=ACTION_CONTRACT_SUBMIT
                                                      if serializer.validated_data['submit']
                                                      else ACTION_CONTRACT_UN_SUBMIT,
                                                      content_object=contract)
            CONTRACT_SUBMIT.send(sender=self.__class__,
                                 contract=contract,
                                 activity_log=activity_log)

            return Response(status=HTTP_200_OK)
        else:
            raise ValidationError(serializer.errors)

    # noinspection PyUnusedLocal
    @action(methods=['PUT', 'PATCH'], detail=True, serializer_class=ApproveSerializer,
            permission_classes=default_perms + [IsSuperuser | (IsConvener &
                                                               ContractNotFinalApproved), ])
    def approve(self, request, pk=None):
        """
        The approve action for course convener to approve contract. Disapprove would cause
        all supervisor's approval be cleared.

        Note that the permission for this class is relatively incomplete, this is to allow
        convener getting details regarding what criteria hasn't meet through database's
        validation error.
        """
        serializer: ApproveSerializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            contract = self.get_object()
            approve_date = serializer.validated_data['approve']

            if approve_date:
                # On approval, set the approval date, and set the convener to the user who
                # is doing the approval action to this contract.
                contract.convener = self.request.user
                contract.convener_approval_date = approve_date
                contract.save()
            else:
                # On disapproval, clear all supervisor approvals. Use atomic as we need to
                # save multiple objects
                with transaction.atomic():
                    contract.convener = None
                    contract.convener_approval_date = None
                    contract.save()
                    for supervise in contract.supervise.all():
                        supervise.supervisor_approval_date = None
                        supervise.save()

            # Log activity, and send signal to trigger notifications
            activity_log = ActivityLog.objects.create(actor=self.request.user,
                                                      action=ACTION_CONTRACT_APPROVE
                                                      if serializer.validated_data['approve']
                                                      else ACTION_CONTRACT_DISAPPROVE,
                                                      message=serializer.validated_data['message'],
                                                      content_object=contract)
            CONTRACT_APPROVE.send(sender=self.__class__,
                                  contract=contract,
                                  activity_log=activity_log)

            return Response(status=HTTP_200_OK)
        else:
            raise ValidationError(serializer.errors)

    # noinspection PyUnusedLocal
    @action(methods=['GET'], detail=True,
            permission_classes=default_perms + [ContractFinalApproved, ])
    def print(self, request, pk=None):
        """
        Return PDF version of given contract, generate one if does not exist.

        TODO: Ideally the file should be upload to somewhere else after generation, rather than
              save to the server's file system. Though be sure to consider concurrent problem in
              that case.
        """
        contract = self.get_object()
        if hasattr(contract, 'individual_project'):
            file_object = None
            try:
                file_object = BytesIO()
                print_individual_project_contract(contract, file_object,
                                                  base_url=request.build_absolute_uri())
                response = HttpResponse(file_object.getvalue(),
                                        content_type='application/pdf')
                response['Content-Disposition'] = 'inline; filename=contract.pdf'
                return response
            except Exception as exc:
                raise exc
            finally:
                file_object.close() if file_object else None
        else:
            return Response('This contract type does not support printing service',
                            status=HTTP_400_BAD_REQUEST)



class AssessmentExamineViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin,
                               DestroyModelMixin, ListModelMixin, NestedGenericViewSet):
    """
    A view the allow users to Create, Retrieve, Update, Delete contract's assessments examiner.
    Also have approval action for examiner to approve assessments.

    Note that this view would be nested inside AssessmentViewSet.
    """

    queryset = AssessmentExamine.objects.all()
    serializer_class = AssessmentExamineSerializer
    permission_classes = default_perms + [AllowSafeMethods | IsSuperuser |
                                          (IsConvener & ContractSubmitted &
                                           ContractNotFinalApproved) |
                                          (IsContractSupervisor & ContractSubmitted &
                                           ContractNotApprovedBySupervisor &
                                           ContractNotFinalApproved & IsExaminerNominator), ]

    def perform_create(self, serializer: AssessmentExamineSerializer):
        """Override the default method to automatically attach relevant objects."""

        self.attach_attributes(serializer)

        return super(AssessmentExamineViewSet, self).perform_create(serializer)

    def perform_update(self, serializer: AssessmentExamineSerializer):
        """Override the default method to automatically attach relevant objects."""

        self.attach_attributes(serializer)

        return super(AssessmentExamineViewSet, self).perform_update(serializer)

    # noinspection PyUnusedLocal
    @action(methods=['PUT', 'PATCH'], detail=True, serializer_class=ApproveSerializer,
            permission_classes=default_perms + [IsSuperuser |
                                                (IsConvener & ContractNotFinalApproved) |
                                                (IsContractAssessmentExaminer &
                                                 ContractApprovedBySupervisor &
                                                 ContractNotFinalApproved), ])
    def approve(self, request, pk=None, parent_lookup_contract=None, parent_lookup_assessment=None):
        """Allow examiners to approve assessments"""

        serializer: ApproveSerializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            assessment_examine: AssessmentExamine = self.get_object()

            # Examiner cannot undo their approval
            if not IsSuperuser.check(request.user) and \
                    not IsConvener.check(request.user) and \
                    assessment_examine.examiner_approval_date:
                raise PermissionDenied('Action on approved item is not allowed, please contact '
                                       'course convener if you need to disapprove.')

            approval_date = serializer.validated_data['approve']
            if approval_date:
                assessment_examine.examiner_approval_date = approval_date
                assessment_examine.save()
            else:
                # Examiner disapprove would clear it's nominator's approval status. However, in the
                # case that the nominator is not one of the contract supervisor, e.g. the supervisor
                # changed, or the examiner was assigned directly by superuser or convener, no
                # approval would be reset, and the convener should be contacted to handle this.
                with transaction.atomic():
                    for supervise in Supervise.objects.filter(
                            supervisor=assessment_examine.examine.nominator,
                            contract=assessment_examine.contract):
                        supervise.supervisor_approval_date = None
                        supervise.save()

            # Log activity, and send signal to trigger notifications
            activity_log = ActivityLog.objects.create(
                    actor=self.request.user,
                    action=ACTION_EXAMINER_APPROVE
                    if serializer.validated_data['approve']
                    else ACTION_EXAMINER_DISAPPROVE,
                    content_object=assessment_examine)
            EXAMINER_APPROVE.send(sender=self.__class__,
                                  assessment_examine=assessment_examine,
                                  activity_log=activity_log)

            return Response(status=HTTP_200_OK)
        else:
            raise ValidationError(serializer.errors)

    def attach_attributes(self, serializer: AssessmentExamineSerializer) -> None:
        """Attach parent object to serializer according to url"""
        serializer.validated_data['assessment'] = self.resolved_parents['assessment']
        serializer.validated_data['contract'] = self.resolved_parents['contract']
        serializer.validated_data['nominator'] = self.request.user


class AssessmentViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin,
                        DestroyModelMixin, ListModelMixin, NestedGenericViewSet):
    """
    A view the allow users to Create, Retrieve, Update, Delete contract's assessments.

    Note that this view would be nested inside ContractViewSet.
    """
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = default_perms + [AllowSafeMethods | IsSuperuser |
                                          (IsContractOwner & ContractNotFinalApproved &
                                           ContractNotSubmitted), ]

    def perform_create(self, serializer):
        """Override the default method to automatically attach relevant objects."""

        serializer.validated_data['contract'] = self.resolved_parents['contract']

        return super(AssessmentViewSet, self).perform_create(serializer)

    def perform_update(self, serializer):
        """Override the default method to automatically attach relevant objects."""

        serializer.validated_data['contract'] = self.resolved_parents['contract']

        # Forbid editing assessment template for individual project
        if not IsSuperuser.check(self.request.user):
            contract = serializer.validated_data['contract']
            if hasattr(contract, 'individual_project') and \
                    serializer.validated_data.get('template', False):
                raise PermissionDenied('Cannot edit template for individual project ')

        return super(AssessmentViewSet, self).perform_update(serializer)


class SuperviseViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin,
                       DestroyModelMixin, ListModelMixin, NestedGenericViewSet):
    """
    A view the allow users to Create, Retrieve, Update, Delete contract's assessments.

    Note that this view would be nested inside ContractViewSet.
    """
    queryset = Supervise.objects.all()
    serializer_class = SuperviseSerializer
    permission_classes = default_perms + [AllowSafeMethods | IsSuperuser |
                                          (IsConvener & ContractSubmitted) |
                                          (IsContractOwner & ContractNotSubmitted &
                                           ContractNotFinalApproved) |
                                          (IsContractFormalSupervisor &
                                           ContractNotApprovedBySupervisor &
                                           ContractNotFinalApproved), ]

    def perform_create(self, serializer: SuperviseSerializer):
        """
        Override the default method to attach relevant objects, and check the nominated
        supervisor is qualified.
        """

        self.attach_attributes(serializer)
        self.check_field_permission(serializer)

        return super(SuperviseViewSet, self).perform_create(serializer)

    def perform_update(self, serializer: SuperviseSerializer):
        """
        Override the default method to attach relevant objects, and check the nominated
        supervisor is qualified.
        """

        self.attach_attributes(serializer)
        self.check_field_permission(serializer)

        return super(SuperviseViewSet, self).perform_update(serializer)

    # noinspection PyUnusedLocal
    @action(methods=['PUT', 'PATCH'], detail=True, serializer_class=ApproveSerializer,
            permission_classes=default_perms + [IsSuperuser |
                                                (IsConvener & ContractSubmitted) |
                                                (IsContractSuperviseOwner & ContractSubmitted), ])
    def approve(self, request, pk=None, parent_lookup_contract=None):
        """Allow supervisor to approve supervise relation"""
        serializer: ApproveSerializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            supervise: Supervise = self.get_object()

            # Supervisor cannot undo their approval
            if not IsSuperuser.check(request.user) and \
                    not IsConvener.check(request.user) and \
                    supervise.supervisor_approval_date:
                raise PermissionDenied('Action on approved item is not allowed, please contact '
                                       'convener if you need to disapprove.')

            # Wrap with transaction since we may need to modify related objects, this would
            # let all related database commits rollback to previous state if any commit fail.
            with transaction.atomic():
                if serializer.validated_data['approve']:
                    supervise.supervisor_approval_date = serializer.validated_data['approve']
                    supervise.save()
                else:
                    # On disapprove, first clear all contract's assessment's approval.
                    # This is because contract owner would be able to modify assessments after
                    # supervisor disapprove, as such examiners should approve again.
                    for assessment_examine in AssessmentExamine.objects.filter(
                            contract=supervise.contract):
                        assessment_examine.examiner_approval_date = None
                        assessment_examine.save()

                    # Clear supervisor's approval
                    supervise.supervisor_approval_date = None
                    supervise.save()

                    # Clear contract's submit status
                    supervise.contract.submit_date = None
                    supervise.contract.save()

            # Log activity, and send signal to trigger notifications
            activity_log = ActivityLog.objects.create(actor=self.request.user,
                                                      action=ACTION_SUPERVISE_APPROVE
                                                      if serializer.validated_data['approve']
                                                      else ACTION_SUPERVISE_DISAPPROVE,
                                                      content_object=supervise)
            SUPERVISE_APPROVE.send(sender=self.__class__,
                                   supervise=supervise,
                                   activity_log=activity_log)

            return Response(status=HTTP_200_OK)
        else:
            raise ValidationError(serializer.errors)

    def attach_attributes(self, serializer: SuperviseSerializer) -> None:
        """Attach automatic attributes according to the request url and content"""

        serializer.validated_data['contract'] = self.resolved_parents['contract']
        serializer.validated_data['nominator'] = self.request.user

        # Check if supervisor is approved, if yes, set the is_formal attribute
        supervisor = serializer.validated_data['supervisor']
        if supervisor.has_perm('research_mgt.can_supervise'):
            serializer.validated_data['is_formal'] = True
        else:
            serializer.validated_data['is_formal'] = False

    def check_field_permission(self, serializer: SuperviseSerializer) -> None:
        """Forbid normal user to nominate unapproved supervisors"""

        requester: SrpmsUser = self.request.user
        if IsSuperuser.check(requester) or IsConvener.check(requester):
            pass  # Superuser and convener can nominate whoever they want as supervisor
        elif IsContractFormalSupervisor.check(self.resolved_parents['contract'],
                                              requester):
            pass  # User with 'can_supervise' permission can nominate whoever they want
        elif serializer.validated_data['is_formal']:
            pass  # User can nominate user who has 'can_supervise' permission as supervisor
        else:
            raise PermissionDenied('Nominate un-approved supervisor is not allowed')
