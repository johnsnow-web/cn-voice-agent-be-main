from django.urls import path


class BaseController:
    """
    BaseController defines URLs by mapping to methods already present in the service.
    """
    
    def __init__(self, service_class):
        """
        Initialize with a service class containing the CRUD logic.
        """
        if not service_class:
            raise ValueError("service_class must be provided.")
        self.service_class = service_class()  

    def get_urls(self):
        """
        Generate URLs by mapping to the service methods.
        """
        model_name = self.service_class.__class__.__name__.replace('Service', '').lower()

        return [
            path('list/', self.service_class.list, name=f'{model_name}_list'),
            path('create/', self.service_class.create, name=f'{model_name}_create'),
            path('get/<uuid:id>/', self.service_class.get_by_id, name=f'{model_name}_retrieve'),
            path('update/<uuid:id>/', self.service_class.update, name=f'{model_name}_update'),
            path('delete/<uuid:id>/', self.service_class.delete, name=f'{model_name}_destroy'),
        ]