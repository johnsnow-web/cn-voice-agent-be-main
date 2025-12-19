from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .user.views import UserViewSet
from .product.views import ProductViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]
