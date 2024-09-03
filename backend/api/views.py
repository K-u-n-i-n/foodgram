from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from api.filters import RecipeFilter
from recipes.models import Favorite, Ingredient, Recipe, Subscription, Tag
from .serializers import (
    AvatarSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserRegistrationSerializer,
    UserSerializer
)


User = get_user_model()


class UserViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return super().get_serializer_class()


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


class SubscriptionListView(ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    pagination_class = None

    # Разобраться с поиском и фильтрацией


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    # permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

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


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None
    filterset_fields = ('name',)
