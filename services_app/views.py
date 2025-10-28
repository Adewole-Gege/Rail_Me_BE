from rest_framework import generics, permissions, status
from .models import Service
from .serializers import ServiceSerializer
from admin_app.views import AdminJWTAuthentication
from rest_framework.response import Response


class ServiceCreateView(generics.CreateAPIView):
    serializer_class = ServiceSerializer
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ServiceListView(generics.ListAPIView):
    serializer_class = ServiceSerializer
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Service.objects.all()


class ServiceDeleteView(generics.DestroyAPIView):
    serializer_class = ServiceSerializer
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        # Only services created by this admin
        return Service.objects.filter(created_by=self.request.user)
        
    def delete(self, request, pk):
        admin_user = request.user

        try:
            service = Service.objects.get(pk=pk)
        except Service.DoesNotExist:
            return Response(
                {"detail": "This service doesn't exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        # check if the admin trying to delete this service is the one who created it
        if service.created_by != admin_user:
            return Response(
                {"detail": "You're not authorized to delete this service."},
                status=status.HTTP_403_FORBIDDEN
            )

        # delete service
        service.delete()
        return Response(
            {"detail": "Service deleted successfully."},
            status=status.HTTP_200_OK
        )
 
        