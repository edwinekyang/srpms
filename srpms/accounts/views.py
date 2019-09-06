from rest_framework import status
from rest_framework import generics
from rest_framework import serializers
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.reverse import reverse as rest_reverse
from django.urls import reverse as djan_reverse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout, get_user_model

from .serializers import LoginSerializer, SrpmsUserSerializer


class APIRootView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({
            'login': rest_reverse('accounts:login', request=request, *args, **kwargs),
            'logout': rest_reverse('accounts:logout', request=request, *args, **kwargs),
            # TODO: add link to user profile in api root
        })


class LoginView(generics.GenericAPIView):
    """
    API View that receives a POST with a user's username and password.
    """

    queryset = get_user_model().objects.all()
    serializer_class = LoginSerializer
    permission_classes = ()  # Remove default permission to allow post action

    def get(self, request: Request):
        if request.user.is_authenticated:
            return redirect(djan_reverse('accounts:user-detail',
                                         args=[request.user.username]))
        else:
            return Response({'detail': 'You\'re not login yet.'}, status.HTTP_401_UNAUTHORIZED)

    def post(self, request: Request, *args, **kwargs):
        serializer: serializers.ModelSerializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = authenticate(request,
                                username=serializer.data['username'],
                                password=serializer.data['password'])
            if user is not None:
                login(request, user)
                return redirect(djan_reverse('accounts:user-detail',
                                             args=[user.username]))

        return Response({'detail': 'Unable to log in with provided credentials'},
                        status=status.HTTP_400_BAD_REQUEST)


class LogoutView(generics.GenericAPIView):
    """
    API View that log the current account out.

    Generally HTTP does not recommend changing the state of the server for GET
    method. However, use GET to logout is common in RESTful apps (though not
    necessarily a best practice).
    """

    def get(self, request: Request):
        if request.user.is_authenticated:
            logout(request)
            return Response({'message': 'You\'ve logout from the current session.'})
        else:
            return Response({'message': 'You\'re not login yet.'}, status.HTTP_401_UNAUTHORIZED)


class UserDetailView(generics.RetrieveAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = SrpmsUserSerializer

    lookup_field = 'username'

    permissions = [permissions.IsAuthenticated]
