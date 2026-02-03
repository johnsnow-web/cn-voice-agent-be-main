from rest_framework.response import Response
from inventory.base.views import BaseView
from inventory.models import Product, Inventory, Category
from .serializers import ProductSerializer
from .services import ProductService

class CategoryViewSet(BaseView):
    queryset = Category.objects.all()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = self.service_class()

class InventoryViewSet(BaseView):
    queryset = Inventory.objects.all()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = self.service_class()

class ProductViewSet(BaseView):
    queryset = Product.objects.get_queryset()
    serializer_class = ProductSerializer
    service_class = ProductService

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = None  # Will be initialized in dispatch

    def dispatch(self, request, *args, **kwargs):

        if request.user and request.user.is_authenticated:
            self.service = self.service_class(user_id=str(request.user.id))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset
        query_params = self.request.query_params

        name = query_params.get('name')
        user_name = query_params.get('userName')
        category_name = query_params.get('categoryName')

        if name:
            queryset = queryset.filter(name__icontains=name)
        if user_name:
            queryset = queryset.filter(user__name=user_name)
        if category_name:
            queryset = queryset.filter(category__name=category_name)
            
        return queryset