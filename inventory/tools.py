from langchain.tools import tool
from inventory.product.services import ProductService
from typing import Dict, Any, Optional

def get_tools(user_id: str):
    service = ProductService(user_id)
    
    @tool
    async def get_products(
        name: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        category: Optional[str] = None,
        unit: Optional[str] = None,
        in_stock: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Fetch products with optional filters.
        
        Args:
            name: Product name to search for (partial match)
            min_price: Minimum price filter
            max_price: Maximum price filter  
            category: Product category name
            unit: Product unit (pcs, kg, etc.)
        
        Returns:
            Dictionary with status, count and products list
        """
        args = {}
        if name is not None:
            args['name'] = name
        if min_price is not None:
            args['min_price'] = min_price
        if max_price is not None:
            args['max_price'] = max_price
        if category is not None:
            args['category'] = category
        if unit is not None:
            args['unit'] = unit
        
        return await service.get_products(args)
    
    @tool
    async def create_product(
        name: str,
        price: float,
        category: str,
        description: Optional[str] = None,
        unit: Optional[str] = None,
        quantity: Optional[int] = None,
        reorderLevel: Optional[int] = None,
        image: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new product in inventory.
        
        Args:
            name: Product name (required)
            price: Product price (required)
            category: Product category (required)
            description: Product description (optional)
            unit: Product unit like pcs, kg (optional, defaults to 'pcs')
            quantity: Initial stock quantity (optional, defaults to 0)
            reorderLevel: Minimum stock level (optional, defaults to 10)
            image: Product image URL (optional)
        
        Returns:
            Dictionary with status, message and created product details
        """
        args = {
            'name': name,
            'price': price,
            'category': category
        }
        if description is not None:
            args['description'] = description
        if unit is not None:
            args['unit'] = unit
        if quantity is not None:
            args['quantity'] = quantity
        if reorderLevel is not None:
            args['reorderLevel'] = reorderLevel
        if image is not None:
            args['image'] = image
            
        return await service.create_product(args)

    @tool
    async def update_product(
        product_id: str,
        name: Optional[str] = None,
        price: Optional[float] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        unit: Optional[str] = None,
        image: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update existing product details.
        
        Args:
            product_id: ID of product to update (required)
            name: New product name (optional)
            price: New product price (optional)
            category: New product category (optional)
            description: New product description (optional)
            unit: New product unit (optional)
            image: New product image URL (optional)
        
        Returns:
            Dictionary with status, message and updated product details
        """
        args = {'product_id': product_id}
        if name is not None:
            args['name'] = name
        if price is not None:
            args['price'] = price
        if category is not None:
            args['category'] = category
        if description is not None:
            args['description'] = description
        if unit is not None:
            args['unit'] = unit
        if image is not None:
            args['image'] = image
            
        return await service.update_product(args)
    
    @tool
    async def delete_product(product_id: str) -> Dict[str, Any]:
        """
        Mark a product as deleted (soft delete).
        
        Args:
            product_id: ID of product to delete (required)
        
        Returns:
            Dictionary with status, message and deleted product details
        """
        args = {'product_id': product_id}
        return await service.delete_product(args)

    @tool
    async def get_inventory(product_id: str) -> Dict[str, Any]:
        """
        Get current inventory levels for a specific product.
        
        Args:
            product_id: ID of product to check inventory (required)
        
        Returns:
            Dictionary with status and inventory details (quantity, reorder level)
        """
        args = {'product_id': product_id}
        return await service.get_inventory(args)
    
    @tool
    async def update_inventory(
        product_id: str,
        quantity: Optional[int] = None,
        reorderLevel: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update inventory quantities and reorder levels.
        
        Args:
            product_id: ID of product to update inventory (required)
            quantity: New stock quantity (optional)
            reorderLevel: New minimum stock level for reordering (optional)
        
        Returns:
            Dictionary with status, message and updated inventory details
        """
        args = {'product_id': product_id}
        if quantity is not None:
            args['quantity'] = quantity
        if reorderLevel is not None:
            args['reorderLevel'] = reorderLevel
            
        return await service.update_inventory(args)
    
    tools = [
        get_products,
        create_product,
        update_product,
        delete_product,
        get_inventory,
        update_inventory
    ]

    # Ensure all tools have proper names
    for tool_obj in tools:
        if not hasattr(tool_obj, 'name'):
            tool_obj.name = tool_obj.func.__name__ if hasattr(tool_obj, 'func') else tool_obj.__name__

    return tools