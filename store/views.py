from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Product, Order, User, Customer
from .serializers import ProductSerializer, OrderSerializer
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
            role=data.get('role', 'customer')
        )
        vendor_id = data.get('vendor_id')
        if vendor_id:
            user.vendor_id = vendor_id
            user.save()

        # Create linked Customer if role is 'customer'
        if user.role == 'customer':
            Customer.objects.create(
                user=user,
                vendor=user.vendor,
                name=data.get('name', user.username)  # fallback to username
            )

        return Response({"msg": "user created"}, status=status.HTTP_201_CREATED)



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
        tenant = getattr(self.request, 'tenant', None) or self.request.user.vendor
        if tenant is None and self.request.user.role == 'admin':
            return Order.objects.all()
        return Order.objects.filter(vendor=tenant)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def place(self, request):
        """
        Place an order as the logged-in customer.
        Automatically assigns customer=request.user and vendor=request.user.vendor.
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save(
            customer=request.user, 
            vendor=request.user.vendor
        )
        return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)
    def get_queryset(self):
        tenant = getattr(self.request, 'tenant', None) or self.request.user.vendor
        if self.request.user.role == 'admin':
            return Order.objects.all()
        if self.request.user.role == 'customer':
            # Only customer's orders
            customer = Customer.objects.filter(user=self.request.user).first()
            return Order.objects.filter(customer=customer)
        return Order.objects.filter(vendor=tenant)


# -----------------------
# JWT Custom Token
# -----------------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['role'] = user.role
        token['tenant_id'] = user.vendor.id if user.vendor else None
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
