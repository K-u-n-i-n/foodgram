from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination
)


class UserLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 6


class RecipesPagination(PageNumberPagination):
    page_size = 6
