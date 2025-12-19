from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class QuerysetPaginator:
    def __init__(self, queryset, request):
        self.queryset = queryset
        self.request = request
        self.page = request.GET.get('page', 1)
        self.per_page = request.GET.get('pageSize', 10)
        try:
            self.per_page = int(self.per_page)
        except ValueError:
            self.per_page = 10

        self.paginator = Paginator(self.queryset, self.per_page)
        try:
            self.page_obj = self.paginator.page(self.page)
        except PageNotAnInteger:
            self.page_obj = self.paginator.page(1)
        except EmptyPage:
            self.page_obj = self.paginator.page(self.paginator.num_pages)

    def get_page(self):
        return self.page_obj

    def get_paginator(self):
        return self.paginator

    def get_paginated_response(self, serializer):
        meta = {
            "total": self.paginator.count,
            "page": self.page_obj.number,
            "pageSize": self.paginator.per_page,
            "totalPages": self.paginator.num_pages,
        }
        return {
            "data": serializer.data,
            "meta": meta
        }
