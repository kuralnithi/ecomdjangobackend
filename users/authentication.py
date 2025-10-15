import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import User

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None

        try:
            # Expect header like: "Bearer <token>"
            prefix, token = auth_header.split(" ")

            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['_id'])
          
            print(auth_header,"auth_header-------")
            print(token,"token-------")
            print(user," authenticated via JWT")
            return (user, token)

        except ValueError:
            raise exceptions.AuthenticationFailed("Invalid authorization header format")
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')
