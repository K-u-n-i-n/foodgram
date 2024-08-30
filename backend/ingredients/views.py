from rest_framework.viewsets import ModelViewSet

from .models import Ingredient
from .serializers import IngredientSerializer


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']
    # filter_fields = ('name',)
    # search_fields = ('name',)
    # ordering_fields = ('name',)
