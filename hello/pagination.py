from rest_framework.pagination import CursorPagination

class DefaultCursorPagination(CursorPagination):
    page_size = 6
    page_size_query_param = None
    ordering = '-created_at'


class CursorSetPagination(CursorPagination):
    page_size = 5
    cursor_query_param = "cursor"
    ordering = "-created_at"