from rest_framework import status
from rest_framework import generics
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.request import Request
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .models import SrpmsUser
from .serializers import SrpmsUserSerializer, LoginSerializer
from .permissions import IsOwnerOrReadOnly


class LoginView(generics.GenericAPIView):
    """
    API View that receives a POST with a user's username and password.
    """

    queryset = User.objects.all()
    serializer_class = LoginSerializer
    permission_classes = ()  # Remove default permission to allow post action

    def post(self, request: Request, *args, **kwargs):
        serializer: serializers.ModelSerializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = authenticate(request,
                                username=serializer.data['username'],
                                password=serializer.data['password'])
            if user is not None:
                login(request, user)
                # TODO: return user profile on success login
                return Response("Successfully login as {}".format(serializer.data['username']))

        return Response("Unable to log in with provided credentials",
                        status=status.HTTP_400_BAD_REQUEST)


class LogoutView(generics.GenericAPIView):
    """
    API View that log the current account out.
    """

    def get(self, request: Request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            return Response("You've logout from the current session.")
        else:
            return Response("You're not login yet.")
