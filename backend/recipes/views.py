from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Favorite, Recipe
from .serializers import RecipeSerializer, FavoriteSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]
    # http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        favorite, created = Favorite.objects.get_or_create(
            user=user, recipe=recipe
        )

        if not created:
            favorite.delete()
            return Response(
                {'status': 'recipe removed from favorites'},
                status=status.HTTP_204_NO_CONTENT
            )

        recipe_data = FavoriteSerializer(
            recipe, context={'request': request}).data

        return Response(recipe_data, status=status.HTTP_201_CREATED)
