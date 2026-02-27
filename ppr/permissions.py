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
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Monitoring yangi narsa qo'sha olmaydi
        if user.role == "monitoring" and request.method == "POST":
            return False

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin yoki superuserga hamma narsa mumkin
        if user.is_superuser or user.role == "admin":
            return True

        if user.role == "monitoring":
            # Ko'rish (GET) hamma uchun ochiq
            if request.method in permissions.SAFE_METHODS:
                return True
            
            # Tahrirlash (PUT, PATCH) faqat o'zining ID si bilan mos kelsa
            return obj.id == user.id

        return True