from .views import ProductViewSet, OrderViewSet, RegisterView, CustomTokenObtainPairView, VendorViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'vendors', VendorViewSet, basename='vendor')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),  # <-- use .as_view()
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('', include(router.urls)),
]
