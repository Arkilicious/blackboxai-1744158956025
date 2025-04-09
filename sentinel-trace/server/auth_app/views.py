from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import logout
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    CACLoginSerializer
)
from .models import CustomUser
import pyotp
from auditlog.models import LogEntry

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate OTP provisioning URI for frontend QR code
            totp = pyotp.TOTP(user.otp_secret)
            provisioning_uri = totp.provisioning_uri(
                name=user.email,
                issuer_name="SentinelTrace"
            )
            return Response({
                'message': 'User registered successfully',
                'otp_uri': provisioning_uri,
                'otp_secret': user.otp_secret
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            # Log login action
            LogEntry.objects.log_action(
                user_id=user.pk,
                content_type_id=None,
                object_id=None,
                object_repr=f"{user.username} logged in",
                action_flag=1,
                change_message="User login"
            )
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

class CACLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = CACLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            # Log CAC login action
            LogEntry.objects.log_action(
                user_id=user.pk,
                content_type_id=None,
                object_id=None,
                object_repr=f"{user.username} logged in via CAC",
                action_flag=1,
                change_message="CAC login"
            )
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # Log logout action
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=None,
                object_id=None,
                object_repr=f"{request.user.username} logged out",
                action_flag=2,
                change_message="User logout"
            )
            
            logout(request)
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
