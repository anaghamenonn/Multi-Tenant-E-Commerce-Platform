# store/middleware.py
from django.utils.deprecation import MiddlewareMixin
from .models import Vendor

class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Option A: tenant from JWT (we ensure token contains tenant_id)
        tenant_id = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            tenant_id = getattr(request.user, 'vendor_id', None)
        # Option B: X-Tenant-ID header
        if not tenant_id:
            tenant_id = request.headers.get('X-Tenant-ID') or request.META.get('HTTP_X_TENANT_ID')
        # Option C (optional): parse subdomain from Host header (left as exercise)
        request.tenant = None
        if tenant_id:
            try:
                request.tenant = Vendor.objects.get(id=tenant_id)
            except Vendor.DoesNotExist:
                request.tenant = None
