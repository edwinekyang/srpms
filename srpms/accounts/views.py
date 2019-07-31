from django.shortcuts import render


def login(request):
    # TODO: Create a login page
    return render(request, 'accounts/login.html')
