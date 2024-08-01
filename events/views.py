from django.db.models import Q
from rest_framework import authentication, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Event
from .serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by("created_at")
    serializer_class = EventSerializer
    authentication_classes = [authentication.TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Event.objects.filter(is_verified=True)
        if user.is_superuser:
            return Event.objects.all()
        return Event.objects.filter(Q(created_by=user) | Q(is_verified=True))

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer()
        serializer.delete(instance, request)
        return Response(status=status.HTTP_204_NO_CONTENT)