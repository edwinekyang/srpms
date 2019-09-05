from rest_framework import status
from rest_framework import generics
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import permissions
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout, get_user_model

from .serializers import LoginSerializer, SrpmsUserSerializer


class LoginView(generics.GenericAPIView):
    """
    API View that receives a POST with a user's username and password.
    """

    queryset = get_user_model().objects.all()
    serializer_class = LoginSerializer
    permission_classes = ()  # Remove default permission to allow post action

    def get(self, request: Request):
        if request.user.is_authenticated:
            return redirect(reverse('accounts:user-detail',
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
                return redirect(reverse('accounts:user-detail',
                                        args=[user.username]))

        return Response({'message': 'Unable to log in with provided credentials'},
                        status=status.HTTP_400_BAD_REQUEST)


class LogoutView(generics.GenericAPIView):
    """
    API View that log the current account out.
    """

    def get(self, request: Request, *args, **kwargs):
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
