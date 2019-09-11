from django.shortcuts import render
from django.http import HttpResponse

from .forms import ContractForm


def contract(request):
    form = ContractForm()
    context = {
        'form': form
    }
    return render(request, 'research_mgt/contract.html', context)


def detail(request, contract_id):
    return HttpResponse("Detail %s" % contract_id)


def result(request, contract_id):
    response = "Manage %s"
    return HttpResponse(response % contract_id)
