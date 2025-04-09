from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import TrackedEntity, TrackingRequest
from .serializers import (
    TrackedEntitySerializer,
    TrackingRequestSerializer,
    TrackingRequestCreateSerializer,
    TrackingRequestUpdateSerializer
)
from auth_app.models import CustomUser

class TrackedEntityViewSet(viewsets.ModelViewSet):
    queryset = TrackedEntity.objects.all()
    serializer_class = TrackedEntitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by search parameters if provided
        identifier_type = self.request.query_params.get('identifier_type')
        if identifier_type:
            queryset = queryset.filter(identifier_type=identifier_type)
        return queryset

class TrackingRequestViewSet(viewsets.ModelViewSet):
    queryset = TrackingRequest.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return TrackingRequestCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TrackingRequestUpdateSerializer
        return TrackingRequestSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Field officers only see their own requests
        if user.role == CustomUser.Role.FIELD_OFFICER:
            return queryset.filter(requester=user)
        
        # Admins/analysts see all requests
        return queryset

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        tracking_request = self.get_object()
        if tracking_request.status != TrackingRequest.Status.PENDING:
            return Response(
                {'error': 'Request is not pending approval'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tracking_request.status = TrackingRequest.Status.APPROVED
        tracking_request.approved_by = request.user
        tracking_request.approved_at = timezone.now()
        tracking_request.save()
        
        return Response(
            TrackingRequestSerializer(tracking_request).data,
            status=status.HTTP_200_OK
        )
