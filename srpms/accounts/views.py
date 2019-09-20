from rest_framework import status
from rest_framework import generics
from rest_framework import serializers
from rest_framework import permissions
from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.reverse import reverse as rest_reverse
from django.urls import reverse as djan_reverse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout, get_user_model

from .serializers import LoginSerializer, SrpmsUserSerializer
from srpms.settings import DEBUG


class APIRootView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def get(self, request, *args, **kwargs):
        pathes = {
            'token': rest_reverse('accounts:token_obtain_pair', request=request, *args, **kwargs),
            'token/refresh': rest_reverse('accounts:token_refresh', request=request, *args,
                                          **kwargs),
            'users': rest_reverse('accounts:user-list', request=request, *args, **kwargs),
        }
        if DEBUG:
            pathes['login'] = rest_reverse('accounts:login', request=request, *args, **kwargs)
            pathes['logout'] = rest_reverse('accounts:logout', request=request, *args, **kwargs)
        return Response(pathes)


class LoginView(generics.GenericAPIView, DeprecationWarning):
    """
    PENDING DEPRECATION, PLEASE DON'T USE FOR PRODUCTION

    API View that receives a POST with a user's username and password.

    If already login, GET would redirect to the user detail view.
    """

    queryset = get_user_model().objects.all()
    serializer_class = LoginSerializer
    permission_classes = ()  # Remove default permission to allow post action

    def post(self, request: Request):
        serializer: serializers.ModelSerializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = authenticate(request,
                                username=serializer.data['username'],
                                password=serializer.data['password'])
            if user is not None:
                login(request, user)
                return redirect(djan_reverse('accounts:user-detail',
                                             args=[user.id]))

        return Response({'detail': 'Unable to log in with provided credentials'},
                        status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(generics.GenericAPIView, DeprecationWarning):
    """
    PENDING DEPRECATION, PLEASE DON'T USE FOR PRODUCTION

    API View that log the current account out.

    Generally HTTP does not recommend changing the state of the server for GET
    method. However, use GET to logout is common in RESTful apps (though not
    necessarily a best practice).
    """
    permission_classes = ()

    def get(self, request: Request):
        if request.user.is_authenticated:
            logout(request)
            return Response({'detail': 'You\'ve logout from the current session.'})
        else:
            return Response({'detail': 'You\'re not login yet.'})


class UserDetailView(generics.RetrieveAPIView):
    """
    Detail view that return user detail in json format, only support GET at the moment.
    """
    queryset = get_user_model().objects.all()
    serializer_class = SrpmsUserSerializer

    permission_classes = [permissions.IsAuthenticated, ]


class UserListView(generics.ListAPIView):
    """
    List view for retrieving user, also support search for user

    Please note that ONLY user exist in this system would be included, this include
    ANU accounts that has used this system (login, nominate, etc.). However, for
    ANU accounts that never interact with this system, it would not be listed.
    """
    queryset = get_user_model().objects.all()
    serializer_class = SrpmsUserSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'first_name', 'last_name', 'uni_id']
