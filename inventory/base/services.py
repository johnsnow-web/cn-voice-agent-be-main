from django.core.exceptions import ValidationError
from typing import Any, Dict
from rest_framework.response import Response
from django.db.models import Q
class BaseService:
    def __init__(self, model_class):
        self.model_class = model_class

    def get_by_id_or_filters(self, filters: Dict[str, Any]) -> Any:
        if 'id' in filters:
            return self.get_by_id(filters['id'])
        queryset = self.model_class.objects.all()
        if hasattr(self.model_class, 'deleted'):
            queryset = queryset.filter(deleted=False)
        queryset = queryset.filter(**filters)
        return queryset.first() if queryset.exists() else None

    def get_queryset(self):
        queryset = self.queryset
        if self.request.query_params:
            filter_conditions = Q()
            for field in self.filterset_fields:
                value = self.request.query_params.get(field)
                if value:
                    filter_conditions &= Q(**{field: value})
            queryset = queryset.filter(filter_conditions)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = queryset, request
        serializer = self.serializer_class(paginator.get_page(), many=True)
        return Response(paginator.get_paginated_response(serializer))

    def create(self, data: Dict[str, Any]) -> Any:
        try:
            instance = self.model_class.objects.create(**data)
            return instance
        except ValidationError as e:
            raise ValidationError(str(e))

    def update(self, filters: Dict[str, Any], data: Dict[str, Any]) -> Any:
        instance = self.get_by_id_or_filters(filters)
        if not instance:
            return {"error": "No matching object found for update."}
        try:
            for key, value in data.items():
                setattr(instance, key, value)
            instance.save()
            # Return a serializable dict instead of the model instance
            return {"status": "success", "id": str(getattr(instance, 'id', None))}
        except Exception as e:
            return {"error": str(e)}

    def delete(self, filters: Dict[str, Any]) -> Any:
        instance = self.get_by_id_or_filters(filters)
        if not instance:
            return {"error": "No matching object found for delete."}
        try:
            if hasattr(instance, 'deleted'):
                instance.deleted = True
                instance.save()
            else:
                instance.delete()
            return {"status": "success", "id": str(getattr(instance, 'id', None))}
        except Exception as e:
            return {"error": str(e)}
