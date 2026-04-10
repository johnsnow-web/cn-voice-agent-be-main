from inventory.models import Category, Product, Inventory
from asgiref.sync import sync_to_async
from django.db.models import Q

class ProductService:
    def __init__(self, user_id):
        self.user_id = user_id
        self.thread_id = None
        self.run_id = None

    @sync_to_async
    def get_products(self, args):
        
        # Start with base query
        query = Q(user_id=self.user_id) & Q(deleted=False)
        
        # Apply filters based on provided arguments
        if 'name' in args:
            query &= Q(name__icontains=args['name'])
        
        if 'min_price' in args:
            query &= Q(price__gte=args['min_price'])
        
        if 'max_price' in args:
            query &= Q(price__lte=args['max_price'])
        
        if 'category' in args:
            query &= Q(category__name__iexact=args['category'])
        
        if 'unit' in args:
            query &= Q(unit=args['unit'])
        
        if 'in_stock' in args and args['in_stock']:
            query &= Q(inventory__quantity__gt=0)
        
        # Execute query
        products = Product.objects.filter(query).select_related('category').distinct()
        
        if not products.exists():
            return {"status": "not_found", "message": "No products matching your criteria"}
        
        # Prepare results
        result = []
        for product in products:
            product_data = {
                "id": str(product.id),
                "name": product.name,
                "price": float(product.price),
                "description": product.description,
                "category": product.category.name,
                "unit": product.unit,
                "image": product.image
            }
            
            # Add inventory info if needed
            if 'in_stock' in args:
                product_data['quantity'] = product.inventory.quantity if hasattr(product, 'inventory') else 0
            
            result.append(product_data)
        
        return {
            "status": "success",
            "count": len(result),
            "products": result
        }

    @sync_to_async
    def create_product(self, args):
        try:
            category, _ = Category.objects.get_or_create(name=args['category'])
            
            product = Product.objects.create(
                user_id=self.user_id,
                category=category,
                name=args['name'],
                price=args['price'],
                description=args.get('description', ''),
                unit=args.get('unit', 'pcs'),
                image=args.get('image')
            )
            
            Inventory.objects.create(
                product=product,
                quantity=args.get('quantity', 0),
                reorderLevel=args.get('reorderLevel', 10)
            )
            
            return {
                "status": "success",
                "message": f"Created product: {product.name} (ID: {product.id})",
                "product": {
                    "id": str(product.id),
                    "name": product.name,
                    "price": float(product.price)
                }
            }
        except Exception as e:
            return {"status": "error", "message": f"Creation failed: {str(e)}"}

    @sync_to_async
    def update_product(self, args):
        try:
            product = Product.objects.get(
                id=args['product_id'],
                user_id=self.user_id,
                deleted=False
            )
            
            changes = []
            original_name = product.name
            
            if 'category' in args:
                old_category = product.category.name
                category, _ = Category.objects.get_or_create(name=args['category'])
                changes.append(f"category: {old_category} → {category.name}")
                product.category = category
            
            for field in ['name', 'price', 'description', 'unit', 'image']:
                if field in args:
                    old_val = getattr(product, field)
                    changes.append(f"{field}: {old_val} → {args[field]}")
                    setattr(product, field, args[field])
            
            product.save()
            
            return {
                "status": "success",
                "message": f"Updated {original_name}: {', '.join(changes)}",
                "product": {
                    "id": str(product.id),
                    "name": product.name,
                    "price": float(product.price),
                    "category": product.category.name
                }
            }
        except Product.DoesNotExist:
            return {"status": "not_found", "message": "Product not found"}
        except Exception as e:
            return {"status": "error", "message": f"Update failed: {str(e)}"}

    @sync_to_async
    def delete_product(self, args):
        try:
            product = Product.objects.get(
                id=args['product_id'],
                user_id=self.user_id,
                deleted=False
            )
            
            product.deleted = True
            product.save()
            
            return {
                "status": "success",
                "message": f"Deleted: {product.name}",
                "product": {
                    "id": str(product.id),
                    "name": product.name
                }
            }
        except Product.DoesNotExist:
            return {"status": "not_found", "message": "Product not found"}
        except Exception as e:
            return {"status": "error", "message": f"Deletion failed: {str(e)}"}

    @sync_to_async
    def get_inventory(self, args):
        try:
            inventory = Inventory.objects.select_related('product').get(
                product_id=args['product_id'],
                product__user_id=self.user_id,
                product__deleted=False
            )
            
            return {
                "status": "success",
                "inventory": {
                    "product_name": inventory.product.name,
                    "quantity": inventory.quantity,
                    "reorderLevel": inventory.reorderLevel
                }
            }
        except Inventory.DoesNotExist:
            return {"status": "not_found", "message": "Inventory not found"}

    @sync_to_async
    def update_inventory(self, args):
        try:
            inventory = Inventory.objects.select_related('product').get(
                product_id=args['product_id'],
                product__user_id=self.user_id,
                product__deleted=False
            )
            
            changes = []
            if 'quantity' in args:
                changes.append(f"quantity: {inventory.quantity} → {args['quantity']}")
                inventory.quantity = args['quantity']
            if 'reorderLevel' in args:
                changes.append(f"reorder level: {inventory.reorderLevel} → {args['reorderLevel']}")
                inventory.reorderLevel = args['reorderLevel']
            
            inventory.save()
            
            return {
                "status": "success",
                "message": f"Inventory updated for {inventory.product.name}: {', '.join(changes)}",
                "product": {
                    "id": str(inventory.product.id),
                    "name": inventory.product.name,
                    "quantity": inventory.quantity,
                    "reorderLevel": inventory.reorderLevel
                }
            }
        except Inventory.DoesNotExist:
            return {"status": "not_found", "message": "Inventory not found"}
        except Exception as e:
            return {"status": "error", "message": f"Inventory update failed: {str(e)}"}
        
