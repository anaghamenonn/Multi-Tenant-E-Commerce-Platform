from rest_framework import permissions

class IsStoreOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'owner'

class IsStaffOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Owner can do everything
        if request.user.role == 'owner':
            return getattr(obj, 'vendor', None) == request.user.vendor
        # Staff can only access assigned objects
        if request.user.role == 'staff':
            return getattr(obj, 'assigned_to', None) == request.user
        return False

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'customer'

class IsVendorObject(permissions.BasePermission):
    """
    Ensure that an object belongs to the tenant (request.tenant or user's vendor)
    and check role-level access for actions.
    """
    def has_object_permission(self, request, view, obj):
        tenant = getattr(request, 'tenant', None) or getattr(request.user, 'vendor', None)
        if tenant is None:
            # allow platform admins (role==admin)
            return request.user.role == 'admin'
        # object must have vendor attribute
        return getattr(obj, 'vendor', None) == tenant
