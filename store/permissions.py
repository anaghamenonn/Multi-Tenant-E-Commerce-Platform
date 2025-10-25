from rest_framework import permissions

class IsStoreOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'owner'

    def has_object_permission(self, request, view, obj):
        # Owner must belong to same vendor to manage vendor-specific objects
        return request.user.is_authenticated and request.user.role == 'owner' and getattr(obj, 'vendor', None) == request.user.vendor


class IsStaffOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('owner', 'staff')

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role == 'owner':
            return getattr(obj, 'vendor', None) == request.user.vendor
        if request.user.role == 'staff':
            return getattr(obj, 'assigned_to', None) == request.user
        return False


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'customer'


class IsVendorObject(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        tenant = getattr(request, 'tenant', None) or getattr(request.user, 'vendor', None)
        if tenant is None:
            return request.user.is_authenticated and request.user.role == 'admin'
        return getattr(obj, 'vendor', None) == tenant
