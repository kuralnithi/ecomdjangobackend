import jwt
import bcrypt
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes,authentication_classes   
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  
from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer, UserLoginSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.utils import timezone
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

import random
import string

@api_view(['POST'])
def register_user(request):
    try:
        print(request.data," in register user")
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Check if user already exists
            if User.objects.filter(username=serializer.validated_data['username']).exists():
                return Response(
                    {'message': 'user already exist'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if User.objects.filter(emailid=serializer.validated_data['emailid']).exists():
                return Response(
                    {'message': 'email already registered'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = serializer.save()
            user_data = UserSerializer(user).data
            
            return Response({
                'message': 'user registered successfully',
                'data': user_data
            })
        else:
            return Response(
                {'message': 'invalid data', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return Response(
            {'message': 'user register failed', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def login_user(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        emailid = serializer.validated_data['emailid']
        password = serializer.validated_data['password']
        print(emailid, password, " in login user")
        user = authenticate(username=emailid, password=password)
        if user is None:
            return Response({"message": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        # Create a custom refresh token
        refresh = RefreshToken.for_user(user)

        # Add user details to token payload
        refresh['id'] = user.id
        refresh['email'] = user.emailid
        refresh['username'] = user.username
        refresh['usertype'] = user.usertype

        return Response({
            "message": "Login successful",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }, status=status.HTTP_200_OK)

    return Response({"message": "Invalid data", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_id(request):
    try:
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'message': 'error in finding user', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def reset_password(request):
    try:
        emailid = request.data.get('emailid')
        
        try:
            user = User.objects.get(emailid=emailid)
        except User.DoesNotExist:
            return Response(
                {'message': 'user not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate reset token
        reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        
        user.resetPasswordToken = reset_token
        user.resetPasswordTokenExpiry = reset_token_expiry
        user.save()
        
        # Send email
        send_mail(
            'PASSWORD RESET MAIL',
            f'reset token: {reset_token}',
            'kuralnithi1999@gmail.com',
            [emailid],
            fail_silently=False,
        )
        
        return Response({'message': 'mail sent successfully to emailid'})
        
    except Exception as e:
        return Response(
            {'message': 'error in resetting password', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def reset_password_page(request):
    try:
        token = request.data.get('token')
        password = request.data.get('password')

        if not token:
            return Response({'message': 'token missing'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(resetPasswordToken=token)
            if user.resetPasswordTokenExpiry < timezone.now():
                return Response({'message': 'token expired'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'message': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(password)
        user.resetPasswordToken = None
        user.resetPasswordTokenExpiry = None
        user.save()

        return Response({'message': 'password reset successful'})

    except Exception as e:
        return Response({'message': 'error in resetting password', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@api_view(['POST'])
def oauth_user(request):
    try:
        token = request.headers.get('Authorization')
        if not token:
            return Response({'message': 'Missing OAuth token'}, status=400)

        token = token.strip('"')

        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request())
            email = idinfo.get('email')
            name = idinfo.get('name')
        except Exception as e:
            return Response({'message': 'Invalid Google token', 'error': str(e)}, status=401)

        user, created = User.objects.get_or_create(
            emailid=email,
            defaults={'username': name, 'usertype': 'customer'},
        )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        serializer = UserSerializer(user)
        msg = 'OAuth user created' if created else 'OAuth user logged in'

        return Response({
            'message': msg,
            'data': serializer.data,
            'access': access_token,
            'refresh': str(refresh),
        })

    except Exception as e:
        return Response({'message': 'OAuth error', 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    user = request.user  # DRF already provides this
    return Response({
        "message": "Token is valid",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.emailid,
            "usertype": user.usertype
        }
    })

@api_view(['POST'])
def refresh_token(request):
    try:
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response(
                {'message': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)

            # Optionally, rotate refresh token (issue a new one)
            new_refresh_token = str(refresh)

            return Response({
                'message': 'Token refreshed successfully',
                'access_token': new_access_token,
                'refresh_token': new_refresh_token,
            }, status=status.HTTP_200_OK)

        except TokenError as e:
            return Response(
                {'message': 'Invalid or expired refresh token', 'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )

    except Exception as e:
        return Response(
            {'message': 'Token refresh failed', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
