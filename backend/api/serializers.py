from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.fields import Base64ImageField
from api.mixins import IsSubscribedMixin
from recipes.models import (Favorite,
                            Ingredient,
                            IngredientInRecipe,
                            Recipe,
                            ShoppingCart,
                            Tag
                            )


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации новых пользователей.
    """

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer, IsSubscribedMixin):
    """
    Сериализатор для представления информации о пользователях.
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )


class RecipeShortSerializer(serializers.ModelSerializer):
    """
    Сериализатор для краткого представления рецептов.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubscriptionSerializer(
        serializers.ModelSerializer, IsSubscribedMixin):
    """
    Сериализатор для отображения информации
    о подписках пользователя на других авторов.
    """

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj)

        if recipes_limit is not None:
            recipes = recipes[:recipes_limit]

        return RecipeShortSerializer(
            recipes, many=True, context=self.context).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с тегами.
    """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class AvatarSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обработки аватара пользователя.
    """

    avatar = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = User
        fields = ['avatar']


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с ингредиентами, использующимися в рецептах.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient.id'
    )
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Основной сериализатор для рецептов.
    """

    cooking_time = serializers.IntegerField(min_value=1)
    image = Base64ImageField(max_length=None, use_url=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredient_in_recipes', many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags.all(), many=True).data
        representation['author'] = UserSerializer(
            instance.author).data

        return representation

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError('Поле не должно быть пустым.')

        ingredient_ids = [ingredient['ingredient']['id']
                          for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Список ингредиентов содержит дубликаты.')

        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError('Поле не должно быть пустым.')

        tag_names = [tag.name for tag in tags]
        if len(tag_names) != len(set(tag_names)):
            raise serializers.ValidationError(
                'Список тегов содержит дубликаты.')

        return tags

    def validate(self, data):

        ingredients = data.get('ingredient_in_recipes', [])
        self.validate_ingredients(ingredients)

        tags = data.get('tags', [])
        self.validate_tags(tags)

        return data

    def create(self, validated_data):

        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredient_in_recipes')

        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['ingredient']['id'],
                amount=ingredient_data['amount']
            )

        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):

        ingredients_data = validated_data.pop('ingredient_in_recipes')
        tags_data = validated_data.pop('tags', None)

        if 'image' in validated_data:
            instance.image = validated_data.get('image', instance.image)

        instance.name = validated_data.get('name', instance.name)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.text = validated_data.get('text', instance.text)
        instance.save()

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            new_ingredients = []

            for ingredient_data in ingredients_data:
                ingredient_obj = ingredient_data.get('ingredient')
                ingredient_instance = ingredient_obj.get(
                    'id') if ingredient_obj else None
                ingredient_id = (
                    ingredient_instance.id if ingredient_instance else None
                )
                amount = ingredient_data.get('amount')

                if ingredient_id is not None:
                    new_ingredients.append((ingredient_id, amount))

            if new_ingredients:
                instance.ingredients.clear()

                for ingredient_id, amount in new_ingredients:
                    IngredientInRecipe.objects.create(
                        recipe=instance,
                        ingredient_id=ingredient_id,
                        amount=amount
                    )
        return instance

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с избранными рецептами.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
