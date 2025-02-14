from rest_framework import permissions
from .models import Article, User

class UserOwnershipPermission(permissions.BasePermission):
    message = "The user isn't the author of this object and can't modify it."

    def has_object_permission(self, request, view, obj: Article):
        return bool(
            request.method in permissions.SAFE_METHODS or
            obj.user == request.user
        )
    

class HasCorrectPermissions(permissions.BasePermission):    
    def has_object_permission(self, request, view, obj):
        map_methods: dict = {"GET": "view", "PUT": "change", "PATCH": "change", "POST": "add", "DELETE": "delete"}
        action = f"{obj._meta.app_label}.{map_methods.get(request.method)}_{obj._meta.model_name}"
        # return super().has_object_permission(request, view, obj)
        permissions: set[str] = request.user.get_all_permissions()
        return permissions.issuperset([action])

class HasRole(permissions.BasePermission):
    def __init__(self, accepted_groups):
        self.accepted_groups = accepted_groups

    def has_permission(self, request, view):
        groups = request.user.groups
        for group in groups:
            if group in self.accepted_groups:
                return True
        return False


class IsReader(permissions.BasePermission):
    message = "Readers can't perform this action."

    def has_permission(self, request, view):
        return request.user.role == User.Role.READER


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.MODERATOR
