from rest_framework.pagination import PageNumberPagination


class AnalyticsPagination(PageNumberPagination):
    """Paginación por defecto de la API: 25 por página, `page_size` configurable."""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100