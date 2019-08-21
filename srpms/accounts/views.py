from rest_framework import status
from rest_framework import generics
from rest_framework import serializers
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
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
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
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
    pass
