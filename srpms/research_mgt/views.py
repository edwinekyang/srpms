from rest_framework.status import HTTP_200_OK
from rest_framework.mixins import (CreateModelMixin, RetrieveModelMixin, UpdateModelMixin,
                                   DestroyModelMixin, ListModelMixin)
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.settings import api_settings
from rest_framework.decorators import action
from rest_framework.serializers import ValidationError
from rest_framework.response import Response

from .mixins import NestedGenericViewSet
from . import serializers
from . import models
from . import permissions as app_perms
from accounts.models import SrpmsUser
from .serializer_utils import SubmitSerializer, ApproveSerializer

# The default settings is set not list
default_perms: list = api_settings.DEFAULT_PERMISSION_CLASSES


class UserViewSet(ReadOnlyModelViewSet):
    """
    Provides read-only user information, as well as the contract they
    involves (own, supervise, convene).
    """
    queryset = SrpmsUser.objects.all()
    serializer_class = serializers.UserContractSerializer


class CourseViewSet(ModelViewSet):
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
            permission_class += [app_perms.ReadOnly |
                                 app_perms.IsSuperuser |
                                 app_perms.IsConvener, ]

        # Below line is from super method
        return [permission() for permission in default_perms]


class AssessmentTemplateViewSet(ModelViewSet):
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
            permission_class += [app_perms.ReadOnly |
                                 app_perms.IsSuperuser |
                                 app_perms.IsConvener, ]

        # Below line is from super method
        return [permission() for permission in default_perms]


class ContractViewSet(ModelViewSet):
    """
    A view the allow users to Create, Read, Update, Delete contracts.
    """
    queryset = models.Contract.objects.all()
    serializer_class = serializers.ContractSerializer
    permission_classes = default_perms + [app_perms.ReadOnly |
                                          app_perms.IsSuperuser |
                                          app_perms.IsContractOwner |
                                          app_perms.IsContractFormalSupervisor, ]

    def perform_create(self, serializer: serializers.ContractSerializer):

        # Set the contract owner to the requester
        serializer.validated_data['owner'] = self.request.user

        return super(ContractViewSet, self).perform_create(serializer)

    @action(methods=['PUT', 'PATCH'], detail=True, serializer_class=SubmitSerializer,
            permission_classes=default_perms + [app_perms.IsSuperuser |
                                                app_perms.IsContractOwner, ])
    def submit(self, request, pk=None):
        # TODO: permission
        serializer: SubmitSerializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            models.Contract.objects.filter(pk=pk).update(
                    submit_date=serializer.validated_data['submit'])
            return Response(status=HTTP_200_OK)
        else:
            raise ValidationError()

    @action(methods=['PUT', 'PATCH'], detail=True, serializer_class=ApproveSerializer,
            permission_classes=default_perms + [app_perms.IsSuperuser |
                                                app_perms.IsConvener, ])
    def approve(self, request, pk=None):
        # TODO: permission
        serializer: ApproveSerializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            models.Contract.objects.filter(pk=pk).update(
                    convener_approval_date=serializer.validated_data['approve'],
                    convener=self.request.user)
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
    permission_classes = default_perms + [app_perms.IsSuperuser |
                                          app_perms.IsConvener |
                                          app_perms.IsContractSupervisor, ]

    def perform_create(self, serializer: serializers.AssessmentExamineSerializer):
        serializer.validated_data['assessment'] = self.resolved_parents['assessment']
        serializer.validated_data['contract'] = self.resolved_parents['contract']
        return super(AssessmentExamineViewSet, self).perform_create(serializer)

    def perform_update(self, serializer):
        serializer.validated_data['assessment'] = self.resolved_parents['assessment']
        serializer.validated_data['contract'] = self.resolved_parents['contract']
        return super(AssessmentExamineViewSet, self).perform_update(serializer)

    @action(methods=['PUT', 'PATCH'], detail=True, serializer_class=ApproveSerializer,
            permission_classes=default_perms + [app_perms.IsSuperuser |
                                                app_perms.IsConvener |
                                                app_perms.IsContractAssessmentExamineOwner, ])
    def approve(self, request, pk=None):
        """Allow examiners to approve assessments"""
        # TODO: permission
        serializer: ApproveSerializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            models.Contract.objects.filter(pk=pk).update(
                    examiner_approval_date=serializer.validated_data['approve'])
            return Response(status=HTTP_200_OK)
        else:
            raise ValidationError()


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
    permission_classes = default_perms + [app_perms.ReadOnly |
                                          app_perms.IsSuperuser |
                                          app_perms.IsConvener |
                                          app_perms.IsContractOwner |
                                          app_perms.IsContractSupervisor, ]


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
    permission_classes = default_perms + [app_perms.ReadOnly |
                                          app_perms.IsSuperuser |
                                          app_perms.IsConvener |
                                          app_perms.IsContractOwner |
                                          app_perms.IsContractFormalSupervisor, ]

    def perform_create(self, serializer: serializers.SuperviseSerializer):

        # Check if supervisor is an approved supervisor, if yes, set the is_form attribute
        supervisor = serializer.validated_data['supervisor']
        if supervisor.has_perm('can_supervise'):
            serializer.validated_data['is_formal'] = True
        else:
            serializer.validated_data['is_formal'] = False

        return super(SuperviseViewSet, self).perform_create(serializer)

    def perform_update(self, serializer: serializers.SuperviseSerializer):

        # Check if supervisor is approved, if yes, set the is_formal attribute
        supervisor = serializer.validated_data['supervisor']
        if supervisor.has_perm('can_supervise'):
            serializer.validated_data['is_formal'] = True
        else:
            serializer.validated_data['is_formal'] = False

        return super(SuperviseViewSet, self).perform_update(serializer)

    @action(methods=['PUT', 'PATCH'], detail=True, serializer_class=ApproveSerializer,
            permission_classes=default_perms + [app_perms.IsSuperuser |
                                                app_perms.IsConvener |
                                                app_perms.IsContractSuperviseOwner, ])
    def approve(self, request, pk=None):
        """Allow supervisor to approve supervise relation"""
        serializer: ApproveSerializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            models.Contract.objects.filter(pk=pk).update(
                    supervisor_approval_date=serializer.validated_data['approve'])
            return Response(status=HTTP_200_OK)
        else:
            raise ValidationError()
