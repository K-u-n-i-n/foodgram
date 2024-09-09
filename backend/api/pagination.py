from rest_framework.pagination import LimitOffsetPagination


class UserLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 6
