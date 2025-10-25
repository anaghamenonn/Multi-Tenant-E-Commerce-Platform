from django.db import models
from django.contrib.auth.models import AbstractUser

class Vendor(models.Model):
    name = models.CharField(max_length=200)
    contact_email = models.EmailField()
    domain = models.CharField(max_length=200, blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLE_CHOICES = (
        ('owner','Store Owner'),
        ('staff','Staff'),
        ('customer','Customer'),
        ('admin','Platform Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.CASCADE)
    # For customers, vendor will be the store they are associated with (or null if global)

class Product(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey('User',null=True,blank=True,limit_choices_to={'role': 'staff'},on_delete=models.SET_NULL,related_name='assigned_products')

class Customer(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='customers')
    user = models.OneToOneField('User', null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)

class Order(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, default='pending') 
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey('User',null=True,blank=True,limit_choices_to={'role': 'staff'},on_delete=models.SET_NULL,related_name='assigned_orders')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
