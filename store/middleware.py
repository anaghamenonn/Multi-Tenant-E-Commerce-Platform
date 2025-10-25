from django.utils.deprecation import MiddlewareMixin
from .models import Vendor

class TenantMiddleware(MiddlewareMixin):
    
    def process_request(self, request):
        tenant_id = None

        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            tenant_id = getattr(user, 'vendor_id', None)

        if not tenant_id:
            tenant_id = request.headers.get('X-Tenant-ID') or request.META.get('HTTP_X_TENANT_ID')

        request.tenant = None
        if tenant_id:
            try:
                request.tenant = Vendor.objects.get(id=tenant_id)
            except Vendor.DoesNotExist:
                request.tenant = None
