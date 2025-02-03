from rest_framework import permissions
from .models import Article

class AuthorshipPermission(permissions.BasePermission):
    message = "The user isn't the author of this object and can't modify it."

    def has_object_permission(self, request, view, obj: Article):
        return bool(
            request.method in permissions.SAFE_METHODS or
            obj.author == request.user
        )
