"""srpms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

__author__ = 'Dajie (Cooper) Yang, and Euikyum (Edwin) Yang'
__credits__ = ['Dajie Yang', 'Euikyum Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse


class APIRootView(APIView):
    """Provide links to apps' api view"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    # noinspection PyMethodMayBeStatic
    def get(self, request, *args, **kwargs):
        return Response({
            'accounts': reverse('accounts:api-root', request=request, *args, **kwargs),
            'research_mgt': reverse('research_mgt:api-root', request=request, *args, **kwargs),
        })


urlpatterns = [
    path('api/', APIRootView.as_view()),
    path('api/admin/', admin.site.urls),
    path('api/research_mgt/', include('research_mgt.urls')),
    path('api/accounts/', include('accounts.urls')),
]

if settings.DEBUG:
    # On development, enable debug toolbar, and serve static and media files from django
    import debug_toolbar

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += [path('api/__debug__/', include(debug_toolbar.urls)), ]
else:
    # On production, static and media files are being served from nginx.
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
