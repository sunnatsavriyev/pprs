from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

class IsAdmin(IsSuperAdmin):
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and
            (user.is_superuser or user.role == "admin")
        )

class IsTarkibiy(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "tarkibiy"

class IsBekat(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "bekat"


class IsBolim(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "bolim"
    
    
class IsMonitoringReadOnly(permissions.BasePermission):
    """
    Monitoring role faqat ko‘rishi mumkin (GET, HEAD, OPTIONS)
    """
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role == "monitoring":
            # Faqat GET, HEAD, OPTIONS
            return request.method in permissions.SAFE_METHODS

        return True 