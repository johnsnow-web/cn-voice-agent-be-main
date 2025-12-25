from rest_framework import viewsets
from rest_framework.response import Response
from ..utils.paginator import QuerysetPaginator
from django.db.models import Q

class BaseView(viewsets.ModelViewSet):
    serializer_class = None
    queryset = None
    filterset_fields = []
    
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
        paginator = QuerysetPaginator(queryset, request)
        serializer = self.serializer_class(paginator.get_page(), many=True)
        return Response(paginator.get_paginated_response(serializer))

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)
