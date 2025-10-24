from rest_framework import serializers
from .models import Vendor, Product, Customer, Order, OrderItem, User

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        read_only_fields = ('vendor',)
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = OrderItem
        fields = ['product', 'qty', 'price']

    def create(self, validated_data):
        product = validated_data['product']
        validated_data['price'] = product.price  # automatically set price
        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'vendor', 'items', 'total_amount', 'status', 'created_at']
        read_only_fields = ['customer', 'vendor', 'total_amount', 'status', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        request = self.context.get('request')
        customer = request.user.customer  # reference the Customer instance
        vendor = request.user.vendor

        order = Order.objects.create(customer=customer, vendor=vendor)

        total = 0
        for item_data in items_data:
            product = item_data['product']
            qty = item_data['qty']
            price = product.price
            OrderItem.objects.create(order=order, product=product, qty=qty, price=price)
            total += price * qty

        order.total_amount = total
        order.save()
        return order
