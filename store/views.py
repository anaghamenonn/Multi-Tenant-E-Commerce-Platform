# store/views.py
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Product, Order, User, Customer, Vendor
from .serializers import ProductSerializer, OrderSerializer, VendorSerializer
from .permissions import IsStoreOwner, IsStaffOrOwner, IsVendorObject

# -----------------------
# User Registration
# -----------------------
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        user = User.objects.create_user(
            username=data['username'],
            password=data['password'],
            role=data.get('role', 'customer'),
            email=data.get('email', '')
        )
        vendor_id = data.get('vendor_id')
        if vendor_id:
            user.vendor_id = vendor_id
            user.save()

        # Create linked Customer if role is 'customer'
        if user.role == 'customer':
            # If vendor is missing, ensure vendor is provided or error
            if not user.vendor:
                # optional: you may choose to allow customer without vendor
                return Response({"detail": "Customer must be associated with a vendor."}, status=status.HTTP_400_BAD_REQUEST)
            Customer.objects.create(
                user=user,
                vendor=user.vendor,
                name=data.get('name', user.username),
                email=data.get('email', user.email or '')
            )

        return Response({"msg": "user created"}, status=status.HTTP_201_CREATED)


# -----------------------
# Vendor API (admin only)
# -----------------------
class VendorViewSet(viewsets.ModelViewSet):
    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated]  # further restrict in methods

    def get_queryset(self):
        # only platform admins can list all vendors
        if self.request.user.is_authenticated and self.request.user.role == 'admin':
            return Vendor.objects.all()
        # otherwise no access
        return Vendor.objects.none()

    def create(self, request, *args, **kwargs):
        # only admin can create vendor
        if not (request.user.is_authenticated and request.user.role == 'admin'):
            return Response({"detail": "Only platform admins can create vendors."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)


# -----------------------
# Products
# -----------------------
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsStaffOrOwner, IsVendorObject]

    def get_queryset(self):
        tenant = getattr(self.request, 'tenant', None) or self.request.user.vendor
        if tenant is None and self.request.user.role == 'admin':
            return Product.objects.all()
        # If staff, show only assigned products in list OR show vendor products for owners
        if self.request.user.role == 'staff':
            return Product.objects.filter(assigned_to=self.request.user)
        return Product.objects.filter(vendor=tenant)

    def perform_create(self, serializer):
        vendor = getattr(self.request, 'tenant', None) or self.request.user.vendor
        serializer.save(vendor=vendor)


# -----------------------
# Orders
# -----------------------
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsStaffOrOwner, IsVendorObject]

    def get_queryset(self):
        # unified get_queryset with role logic
        tenant = getattr(self.request, 'tenant', None) or self.request.user.vendor
        if self.request.user.role == 'admin':
            return Order.objects.all()
        if self.request.user.role == 'customer':
            customer = Customer.objects.filter(user=self.request.user).first()
            if not customer:
                return Order.objects.none()
            return Order.objects.filter(customer=customer)
        if self.request.user.role == 'staff':
            return Order.objects.filter(assigned_to=self.request.user)
        return Order.objects.filter(vendor=tenant)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def place(self, request):
        """
        Place an order as the logged-in customer.
        Request user must be role=customer; OrderSerializer will set customer/vendor.
        """
        if request.user.role != 'customer':
            return Response({"detail": "Only customers can place orders."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        out_serializer = OrderSerializer(order, context={'request': request})
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)


# -----------------------
# JWT Custom Token (already present)
# -----------------------
class CustomTokenObtainPairView(TokenObtainPairView):
    from .token_serializers import MyTokenObtainPairSerializer
    serializer_class = MyTokenObtainPairSerializer
