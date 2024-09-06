from collections import defaultdict
import csv
from io import StringIO
import os

import hashids
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from dotenv import load_dotenv, find_dotenv
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, ParseError
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly
                                        )
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from api.filters import RecipeFilter
from api.permissions import IsAuthorOrAdmin
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag
)
from .serializers import (
    AvatarSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserSubscriptionSerializer
)


User = get_user_model()

load_dotenv(find_dotenv())

BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:8000')


class UserViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return super().get_serializer_class()

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        target_user = self.get_object()
        current_user = request.user

        if request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=current_user, author=target_user
            ).first()

            if not subscription:
                return Response(
                    {"detail": "Подписка не найдена."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if target_user == current_user:
            return Response(
                {"detail": "Нельзя подписаться на самого себя."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Subscription.objects.filter(
                user=current_user, author=target_user).exists():
            return Response(
                {"detail": "Вы уже подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST
            )

        Subscription.objects.create(user=current_user, author=target_user)

        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
            except ValueError:
                raise ParseError("Параметр recipes_limit должен быть числом.")

        context = self.get_serializer_context()
        context['recipes_limit'] = recipes_limit

        user_data = UserSubscriptionSerializer(
            target_user, context=context).data
        return Response(user_data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        user = request.user

        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
            except ValueError:
                raise ParseError("Параметр recipes_limit должен быть числом.")

        subscriptions = Subscription.objects.filter(
            user=user).select_related('author')
        authors = [subscription.author for subscription in subscriptions]

        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = UserSubscriptionSerializer(
                page, many=True,
                context={'request': request, 'recipes_limit': recipes_limit}
            )
            return self.get_paginated_response(serializer.data)

        serializer = UserSubscriptionSerializer(
            authors, many=True,
            context={'request': request, 'recipes_limit': recipes_limit}
        )
        return Response(serializer.data)


class UserSelfView(APIView):
    """
    Представление для получения данных
    текущего пользователя.

    Доступно только для аутентифицированных пользователей.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if 'avatar' not in request.data:
            return Response(
                {'avatar': 'Это поле обязательно для заполнения.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()

        return Response({
            'avatar': request.build_absolute_uri(user.avatar.url)
        }, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrAdmin]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    # Избыточен, добавление в закладки
    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, partial=True, **kwargs)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            favorite, created = Favorite.objects.get_or_create(
                user=user, recipe=recipe
            )

            if not created:
                raise ValidationError(
                    {'detail': 'Рецепт уже есть в избранном'}
                )

            recipe_data = FavoriteSerializer(
                recipe, context={'request': request}
            ).data
            return Response(recipe_data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            favorite = Favorite.objects.filter(
                user=user, recipe=recipe).first()

            if not favorite:
                return Response(
                    {'detail': 'Рецепт не найден в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            shopping_cart, created = ShoppingCart.objects.get_or_create(
                user=user, recipe=recipe
            )

            if not created:
                raise ValidationError(
                    {'detail': 'Рецепт уже находится в корзине покупок'}
                )

            recipe_data = FavoriteSerializer(
                recipe, context={'request': request}
            ).data
            return Response(recipe_data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            shopping_cart = ShoppingCart.objects.filter(
                user=user, recipe=recipe).first()

            if not shopping_cart:
                return Response(
                    {'detail': 'Рецепт не найден в корзине покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        hashid = hashids.Hashids(salt="random_salt", min_length=8)
        short_id = hashid.encode(recipe.id)
        short_link = f'{BASE_URL}/s/{short_id}'
        return Response({"short-link": short_link})

    @action(
        detail=False,
        methods=['get'],
        url_path='resolve-link/(?P<short_id>[^/.]+)'
    )
    def resolve_link(self, request, short_id):
        hashid = hashids.Hashids(salt="random_salt", min_length=8)
        decoded = hashid.decode(short_id)
        if not decoded:
            return Response({"error": "Invalid short link"}, status=400)

        recipe_id = decoded[0]
        recipe = Recipe.objects.filter(id=recipe_id).first()
        if not recipe:
            return Response({"error": "Recipe not found"}, status=404)
        return Response(
            {"id": recipe.id,
             "name": recipe.name,
             "description": recipe.description}
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart_items = ShoppingCart.objects.filter(user=user)
        ingredient_totals = defaultdict(lambda: {'amount': 0, 'unit': ''})

        for item in shopping_cart_items:
            recipe = item.recipe
            for ri in recipe.ingredientinrecipe_set.all():
                ingredient_name = ri.ingredient.name
                unit = ri.ingredient.measurement_unit
                ingredient_totals[ingredient_name]['amount'] += ri.amount
                ingredient_totals[ingredient_name]['unit'] = unit

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Ингредиенты', 'Количество'])

        for ingredient, data in ingredient_totals.items():
            amount = data['amount']
            unit = data['unit']
            writer.writerow([f'{ingredient} ({unit})', f'{amount}'])

        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.csv"'
        )
        return response


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    pagination_class = None
    filterset_fields = ('name',)
    search_fields = ('^name',)
