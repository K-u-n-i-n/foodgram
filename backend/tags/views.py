# from rest_framework import filters
from rest_framework.viewsets import ModelViewSet

from .models import Tag
from .serializers import TagSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    # Разобраться с поиском и фильтрацией
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('^slug',)
    lookup_field = 'slug'
