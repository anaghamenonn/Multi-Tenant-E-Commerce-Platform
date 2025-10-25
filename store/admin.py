from django.contrib import admin
from .models import Vendor, User, Product, Customer, Order, OrderItem


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "contact_email", "domain", "created_at")
    search_fields = ("name", "contact_email", "domain")
    list_filter = ("created_at",)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "vendor", "is_active", "is_staff")
    list_filter = ("role", "vendor", "is_active")
    search_fields = ("username", "email")
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Vendor Info", {"fields": ("role", "vendor")}),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "vendor", "price", "quantity", "assigned_to", "created_at")
    list_filter = ("vendor",)
    search_fields = ("name", "sku")
    autocomplete_fields = ("vendor", "assigned_to")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "vendor", "phone")
    list_filter = ("vendor",)
    search_fields = ("name", "email")
    autocomplete_fields = ("vendor", "user")


# ---------------- Order ----------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "vendor", "customer", "total_amount", "status", "assigned_to", "created_at")
    list_filter = ("vendor", "status")
    search_fields = ("id", "customer__name")
    autocomplete_fields = ("vendor", "customer", "assigned_to")
    inlines = [OrderItemInline]


# ---------------- OrderItem ----------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "qty", "price")
    autocomplete_fields = ("order", "product")
