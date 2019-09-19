from rest_framework import viewsets
from rest_framework import permissions
from django.shortcuts import render
from django.http import HttpResponse

from .forms import ContractForm
from .serializers import UserContractSerializer, AssessmentMethodSerializer
from .models import AssessmentMethod
from accounts.models import SrpmsUser


def index(request):
    form = ContractForm()
    context = {
        'form': form
    }
    return render(request, 'research_mgt/index.html', context)


def detail(request, contract_id):
    return HttpResponse("Detail %s" % contract_id)


def result(request, contract_id):
    response = "Manage %s"
    return HttpResponse(response % contract_id)


class AssessmentMethodViewSet(viewsets.ModelViewSet):
    queryset = AssessmentMethod.objects.all()
    serializer_class = AssessmentMethodSerializer
    permission_classes = [permissions.IsAuthenticated, ]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = SrpmsUser.objects.all()
    serializer_class = UserContractSerializer
    permission_classes = [permissions.IsAuthenticated, ]
