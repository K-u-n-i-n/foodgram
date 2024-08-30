from rest_framework import serializers

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
    tags = TagSerializer(read_only=True, many=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)
