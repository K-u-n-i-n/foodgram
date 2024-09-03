import base64
import imghdr
import uuid

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import (Favorite,
                            Ingredient,
                            IngredientInRecipe,
                            Recipe,
                            ShoppingCart,
                            Subscription,
                            Tag
                            )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            img_data = base64.b64decode(imgstr)

            file_name = f"{uuid.uuid4()}.{ext}"

            if not imghdr.what(None, img_data):
                raise serializers.ValidationError('Неверное изображение')

            data = ContentFile(img_data, name=file_name)

        return super().to_internal_value(data)


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
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


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        # Проверить наличие подписки в другой таблице
        return False


class TagSerializer(serializers.ModelSerializer):
    # Настроить валидатор ^[-a-zA-Z0-9_]+$ для тегов

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = User
        fields = ['avatar']


class IngredientInRecipeSerializer(serializers.ModelSerializer):

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

    cooking_time = serializers.IntegerField(min_value=1)
    image = Base64ImageField(max_length=None, use_url=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredientinrecipe_set', many=True
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

    def validate(self, data):
        ingredients = data.get('ingredientinrecipe_set', [])

        if not ingredients and not self.instance:
            raise serializers.ValidationError(
                {'ingredients': 'Поле не должно быть пустым.'}
            )

        if ingredients:
            ingredient_ids = [ingredient['ingredient']['id']
                              for ingredient in ingredients]
            if len(ingredient_ids) != len(set(ingredient_ids)):
                raise serializers.ValidationError(
                    {'ingredients': 'Список ингредиентов содержит дубликаты.'}
                )
        tags = data.get('tags', [])

        if not tags and not self.instance:
            raise serializers.ValidationError(
                {'tags': 'Поле не должно быть пустым.'}
            )

        if tags:
            tag_names = [tag.name for tag in tags]
            if len(tag_names) != len(set(tag_names)):
                raise serializers.ValidationError(
                    {'tags': 'Список тегов содержит дубликаты.'}
                )

        return data

    def create(self, validated_data):

        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredientinrecipe_set')

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
        """Переопределение метода update."""

        ingredients_data = validated_data.pop('ingredientinrecipe_set')
        tags_data = validated_data.pop('tags', None)

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
        # Проверить код.
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


#  Получить короткую ссылку на рецепт


class SubscriptionSerializer(serializers.ModelSerializer):
    recipes = RecipeSerializer(
        many=True, read_only=True, source='author.recipe_set'
    )
    recipes_count = serializers.SerializerMethodField()
    avatar = AvatarSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    # def get_avatar(self, obj):
    #     return obj.author.profile.avatar.url if hasattr(obj.author, 'profile') else None


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
