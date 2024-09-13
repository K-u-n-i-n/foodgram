from rest_framework import status
from rest_framework.response import Response

from recipes.models import Subscription


class IsSubscribedMixin:
    """
    Миксин для проверки подписки пользователя на автора.
    """

    def get_is_subscribed(self, obj):
        request = self.context.get('request')

        if request and hasattr(
            request, 'user'
        ) and request.user.is_authenticated:

            return Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()

        return False


class RecipeActionMixin:
    """
    Миксин для добавления или удаления рецепта в/из избранного или корзины.
    """

    def check_recipe_action(self, request, model, serializer_class):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            obj, created = model.objects.get_or_create(
                user=user, recipe=recipe)

            if not created:
                return Response(
                    {'detail': 'Такой рецепт уже присутствует'},
                    status=status.HTTP_409_CONFLICT
                )

            data = serializer_class(recipe, context={'request': request}).data
            return Response(data, status=status.HTTP_201_CREATED)

        obj = model.objects.filter(user=user, recipe=recipe).first()

        if not obj:
            return Response(
                {'detail': 'Рецепт не найден.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
