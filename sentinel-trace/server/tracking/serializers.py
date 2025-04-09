from rest_framework import serializers
from .models import TrackedEntity, TrackingRequest
from auth_app.models import CustomUser

class TrackedEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackedEntity
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class TrackingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingRequest
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'requester', 'approved_by', 'approved_at')

class TrackingRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingRequest
        fields = ['tracked_entity', 'purpose', 'duration_days']
        
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['requester'] = request.user
        return super().create(validated_data)

class TrackingRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingRequest
        fields = ['status', 'rejection_reason']
