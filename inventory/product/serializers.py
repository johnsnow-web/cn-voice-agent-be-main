from rest_framework import serializers
from inventory.models import Product

class ProductSerializer(serializers.ModelSerializer):
    userId = serializers.UUIDField(source='user.id')
    userName = serializers.CharField(source='user.name')
    categoryId = serializers.UUIDField(source='category.id')
    categoryName = serializers.CharField(source='category.name')
    quantity = serializers.SerializerMethodField()
    reorderLevel = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = '__all__'

    def get_quantity(self, obj):
        inv = obj.inventory.first()  
        return inv.quantity if inv else None

    def get_reorderLevel(self, obj):
        inv = obj.inventory.first()
        return inv.reorderLevel if inv else None
