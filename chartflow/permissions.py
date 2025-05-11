from rest_framework.permissions import BasePermission

class UserViewPermissions(BasePermission):
    def has_permission(self, request, view):
        if view.action in ["retrieve", "partial_update", "me"]:
            return True
        
        return False
        
    def has_object_permission(self, request, view, obj):
        if view.action in ["retrieve", "partial_update"]:
            return obj == request.user

        return False

class ArtistViewPermissions(BasePermission):
    def has_permission(self, request, view):
        if view.action in ["retrieve", "partial_update", "performance", "nationalities", "list"]:
            return True
        
        return False
        
    def has_object_permission(self, request, view, obj):
        if view.action in ["retrieve", "performance"]:
            if request.user.role == "artist":
                return obj == request.user.artist_profile
            elif request.user.role == "manager":
                return obj in request.user.managed_artists.all()
        elif view.action == "partial_update":
            if request.user.role == "artist":
                return obj == request.user.artist_profile
        return False

class CountryViewPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.user.role in ["admin","manager"] and view.action in ["list", "retrieve"]:
            return True
        
        return False
        
    def has_object_permission(self, request, view, obj):
        if view.action == "retrieve":
            return True
        
        return False

class ChartViewPermissions(BasePermission):
    def has_permission(self, request, view):
        if view.action in ["list", "retrieve", "countries", "by_country"]:
            return True
        
        return False
        
    def has_object_permission(self, request, view, obj):
        if view.action == "retrieve":
            return True
        
        return False

class ChartEntryViewPermissions(BasePermission):
    def has_permission(self, request, view):
        if view.action in ["list", "retrieve"]:
            return True
        
        return False
        
    def has_object_permission(self, request, view, obj):
        if view.action == "retrieve":
            return True
        
        return False

class CountryClusterViewPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.user.role in ["admin","manager"] and view.action in ["list", "retrieve"]:
            return True
        
        return False
        
    def has_object_permission(self, request, view, obj):
        if view.action == "retrieve":
            return True
        
        return False