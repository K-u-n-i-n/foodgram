from rest_framework import serializers

from users.serializers import UserSerializer
from tags.models import Tag
from core.serializers import Base64ImageField
from ingredients.models import Ingredient
from tags.serializers import TagSerializer
from .models import IngredientInRecipe, Recipe


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
    
#  Получить короткую ссылку на рецепт
