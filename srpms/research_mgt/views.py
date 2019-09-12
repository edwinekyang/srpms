from rest_framework import generics, permissions, viewsets
from accounts.permissions import IsOwnerOrReadOnly
from .models import Course, Contract
from research_mgt.serializers import CourseSerializer, ContractSerializer


class CourseList(generics.ListAPIView):
    """
    List all courses.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class ContractViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(u_id=self.request.user)
