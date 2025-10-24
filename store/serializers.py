# store/serializers.py
from rest_framework import serializers
from .models import Vendor, Product, Customer, Order, OrderItem, User

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='staff'), allow_null=True, required=False)

    class Meta:
        model = Product
        read_only_fields = ('vendor',)
        fields = '__all__'

    def validate_assigned_to(self, value):
        if value is None:
            return value
        # staff must belong to same vendor
        vendor = self.context.get('request').user.vendor or getattr(self.context.get('request'), 'tenant', None)
        if value.vendor != vendor:
            raise serializers.ValidationError("Assigned staff must belong to the same vendor.")
        return value

    def create(self, validated_data):
        vendor = getattr(self.context.get('request'), 'tenant', None) or self.context.get('request').user.vendor
        validated_data['vendor'] = vendor
        return super().create(validated_data)

class OrderItemSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'qty', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    # Expose items read-only nested output if needed
    items_detail = OrderItemSerializer(source='items', many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'vendor', 'items', 'items_detail', 'total_amount', 'status', 'created_at', 'assigned_to']
        read_only_fields = ['customer', 'vendor', 'total_amount', 'status', 'created_at']

    def validate(self, data):
        # ensure products in items belong to the same vendor as requester
        request = self.context.get('request')
        vendor = getattr(request, 'tenant', None) or request.user.vendor
        for item in data.get('items', []):
            product = item['product']
            if product.vendor != vendor:
                raise serializers.ValidationError("Product {} does not belong to your vendor.".format(product.id))
        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        request = self.context.get('request')
        # find or create customer object for request.user
        customer = None
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            # If user is customer role, create Customer; otherwise error
            if request.user.role == 'customer':
                customer = Customer.objects.create(user=request.user, vendor=request.user.vendor, name=request.user.username, email=request.user.email or '')
            else:
                raise serializers.ValidationError("No customer associated with this user.")

        vendor = getattr(request, 'tenant', None) or request.user.vendor
        order = Order.objects.create(customer=customer, vendor=vendor)

        total = 0
        for item in items_data:
            product = item['product']
            qty = item['qty']
            price = product.price
            OrderItem.objects.create(order=order, product=product, qty=qty, price=price)
            total += price * qty

        order.total_amount = total
        order.save()
        return order
