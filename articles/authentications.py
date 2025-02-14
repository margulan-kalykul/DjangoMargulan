from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object
from rest_framework import authentication, exceptions
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.models import TokenUser
from .models import User
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomTokenUser(TokenUser):
    @property
    def groups(self) -> list[str]:
        return self.token['groups']


class RoleAuthentication(JWTAuthentication):
    def get_user(self, validated_token) -> CustomTokenUser:
        try:
            validated_token['user_id']
        except KeyError:
            raise InvalidToken("Token contained no recognizable user identification")
        user = CustomTokenUser(validated_token)
        return user
    

# class ModeratorAuthentication(authentication.BaseAuthentication):
#     def authenticate(self, request):
#         token_str = request.headers.get('Authorization').replace('Bearer ', '')
#         if not token_str:
#             return None

#         try:
#             access_token = AccessToken(token_str)
#             user = User.objects.get(pk=access_token['user_id'])
#             role = access_token['role']
#         except Exception:
#             raise exceptions.AuthenticationFailed('Token decoding failed.')

#         if role == User.Role.MODERATOR:
#             return (user, access_token)
#         return exceptions.AuthenticationFailed('You are not authenticated to perform this action.')
