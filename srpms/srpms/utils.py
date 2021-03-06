"""
Custom exception handling, so that we can convert exceptions like ValidationError to 4xx response.
By default they would be come 5xx server error if not handled correctly.
"""

__author__ = 'Dajie (Cooper) Yang'
__credits__ = ['Dajie Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from typing import Dict
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc: Dict, context):
    """
    Custom exception handling, we don't want the server return 500 when validation
    failed on database model.

    https://www.django-rest-framework.org/api-guide/exceptions/#custom-exception-handling

    Args:
        exc: exception raised internally
        context: the context of that exception, might be anything, refer to the link
                 above for details
    """
    response = exception_handler(exc, context)

    if not response and isinstance(exc, ValidationError):
        data = exc.message_dict
        data['detail'] = 'Validation Error'

        response = Response(data, status.HTTP_400_BAD_REQUEST)

    return response
