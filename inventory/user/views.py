from inventory.base.views import BaseView
from inventory.models import User
from .serializers import UserSerializer
from .services import UserService

class UserViewSet(BaseView):
    queryset = User.objects.get_queryset()
    serializer_class = UserSerializer
    service_class = UserService

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = self.service_class()