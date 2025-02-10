from rest_framework import permissions
from .models import Article

class AuthorshipPermission(permissions.BasePermission):
    message = "The user isn't the author of this object and can't modify it."

    def has_object_permission(self, request, view, obj: Article):
        return bool(
            request.method in permissions.SAFE_METHODS or
            obj.author == request.user
        )
    

class HasRolePermission(permissions.BasePermission):    
    def has_object_permission(self, request, view, obj):
        map_methods: dict = {"GET": "view", "PUT": "change", "PATCH": "change", "POST": "add", "DELETE": "delete"}
        action = f"{obj._meta.app_label}.{map_methods.get(request.method)}_{obj._meta.model_name}"
        # return super().has_object_permission(request, view, obj)
        permissions: set[str] = request.user.get_all_permissions()
        return permissions.issuperset([action])


class IsAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='author').exists()


class IsModerator(permissions.BasePermission):
    message = "Moderators can't perform this action."

    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderator').exists()
