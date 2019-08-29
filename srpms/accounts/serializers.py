from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator

from .models import SrpmsUser


class SrpmsUserSerializer(serializers.HyperlinkedModelSerializer):
    """
    For serializing the SRPMSUser model.
    """

    # The model by default include a url fields "<model_name>-detail", in this case would
    # be srpms-user-detail. However, it does not specify the name space, hence we need to
    # manually specify here.
    url = serializers.HyperlinkedIdentityField(view_name="accounts:srpms-user-detail")

    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    email = serializers.ReadOnlyField(source='user.email')

    # Specify fields that would serialize
    class Meta:
        model = SrpmsUser
        fields = ['url', 'id', 'uni_id', 'first_name', 'last_name', 'auth_method',
                  'email', 'contact_email']


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

        extra_kwargs = {
            'username': {
                # Remove unique validation over username field, since we are using it
                # to login instead of creating new user
                'validators': [UnicodeUsernameValidator()],
            },
            'password': {
                # Add mask for password
                'style': {'input_type': 'password'},
            }
        }
