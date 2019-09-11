from rest_framework import generics, permissions
from accounts.permissions import IsOwnerOrReadOnly
from .models import Course, Contract
from research_mgt.serializers import CourseSerializer, ContractSerializer


class CourseList(generics.ListAPIView):
    """
    List all courses.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class ContractList(generics.ListCreateAPIView):
    """
    List all contracts, or create a new contract.
    """
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(u_id=self.request.user)


class ContractDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a contract instance.
    """
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
