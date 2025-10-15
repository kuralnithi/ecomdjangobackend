import jwt
import bcrypt
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer, UserLoginSerializer
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
    try:
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            emailid = serializer.validated_data['emailid']
            password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(emailid=emailid)
            except User.DoesNotExist:
                return Response(
                    {'message': 'user not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if not user.check_password(password):
                return Response(
                    {'message': 'invalid user password'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Generate JWT token
            token = jwt.encode(
                {'_id': user.id, 'exp': datetime.utcnow() + timedelta(days=7)},
                settings.JWT_SECRET_KEY,
                algorithm='HS256'
            )
            
            return Response({
                'message': 'Login successfully',
                'token': token
            })
        else:
            return Response(
                {'message': 'invalid data', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return Response(
            {'message': 'invalid user', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

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
            return Response(
                {'message': 'token missing'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(resetPasswordToken=token)
            if user.resetPasswordTokenExpiry < datetime.utcnow():
                return Response(
                    {'message': 'token expired'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            return Response(
                {'message': 'user not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        user.set_password(password)
        user.resetPasswordToken = None
        user.resetPasswordTokenExpiry = None
        user.save()
        
        return Response({'message': 'password reset successful'})
        
    except Exception as e:
        return Response(
            {'message': 'error in resetting password', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def oauth_user(request):
    try:
        credentials = request.user  # Set by OAuth middleware
        usertype = request.data.get('usertype', 'customer')
        
        # Check if user already exists
        try:
            user = User.objects.get(username=credentials['name'])
            serializer = UserSerializer(user)
            return Response({
                'message': 'Oauth- user found in database',
                'data': serializer.data
            })
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create(
                username=credentials['name'],
                emailid=credentials['email'],
                usertype=usertype
            )
            serializer = UserSerializer(user)
            
            return Response({
                'message': 'new Oauth user created successfully',
                'data': serializer.data
            })
            
    except Exception as e:
        return Response(
            {'message': 'error in OAuth user creation or login', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )