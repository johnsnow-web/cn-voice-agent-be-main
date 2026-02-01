from inventory.base.services import BaseService
from inventory.models import User
from typing import Dict, Optional

class UserService(BaseService):
    def __init__(self):
        super().__init__(User)

    def list(self, filters: Optional[Dict] = None):
        """
        List users with their related products count
        """
        queryset = super().list(filters)
        
