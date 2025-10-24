# store/permissions.py
from rest_framework import permissions

class IsStoreOwner(permissions.BasePermission):
    """
    Owner of the vendor. has_permission used for list/create actions by owner.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'owner'

    def has_object_permission(self, request, view, obj):
        # Owner must belong to same vendor to manage vendor-specific objects
        return request.user.is_authenticated and request.user.role == 'owner' and getattr(obj, 'vendor', None) == request.user.vendor


class IsStaffOrOwner(permissions.BasePermission):
    """
    For staff: allow object-level actions only if assigned_to == request.user.
    For owner: allow actions across vendor objects.
    This permission supports both list-level and object-level checks.
    """
    def has_permission(self, request, view):
        # Basic allow for authenticated staff/owner to reach view-level (detailed checks in object level)
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
    """
    Ensure that the object belongs to the tenant (request.tenant or request.user.vendor).
    Platform admins (role == 'admin') are allowed to bypass vendor check.
    """
    def has_object_permission(self, request, view, obj):
        tenant = getattr(request, 'tenant', None) or getattr(request.user, 'vendor', None)
        if tenant is None:
            # allow platform admins (role==admin)
            return request.user.is_authenticated and request.user.role == 'admin'
        return getattr(obj, 'vendor', None) == tenant
