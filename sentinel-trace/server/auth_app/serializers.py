from rest_framework import serializers
from django.contrib.auth import authenticate
from django_otp.plugins.otp_totp.models import TOTPDevice
from .models import CustomUser
import pyotp

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'role', 'cac_id']
        extra_kwargs = {
            'password': {'write_only': True},
            'cac_id': {'required': False}
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', CustomUser.Role.FIELD_OFFICER),
            cac_id=validated_data.get('cac_id')
        )
        # Generate OTP secret for 2FA
        user.otp_secret = pyotp.random_base32()
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    otp_code = serializers.CharField(required=False)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        
        if not user.is_verified and user.role != CustomUser.Role.FIELD_OFFICER:
            raise serializers.ValidationError("Account not verified")
        
        # Verify OTP if enabled
        if user.otp_secret and not data.get('otp_code'):
            raise serializers.ValidationError("OTP code required")
        
        if user.otp_secret and data.get('otp_code'):
            totp = pyotp.TOTP(user.otp_secret)
            if not totp.verify(data['otp_code']):
                raise serializers.ValidationError("Invalid OTP code")
        
        return {
            'user': user,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }

class CACLoginSerializer(serializers.Serializer):
    cac_id = serializers.CharField()
    otp_code = serializers.CharField()

    def validate(self, data):
        try:
            user = CustomUser.objects.get(cac_id=data['cac_id'])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Invalid CAC ID")
        
        # Verify OTP
        if not user.otp_secret:
            raise serializers.ValidationError("2FA not configured")
        
        totp = pyotp.TOTP(user.otp_secret)
        if not totp.verify(data['otp_code']):
            raise serializers.ValidationError("Invalid OTP code")
        
        return {
            'user': user,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
