from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from ingredients.models import Ingredient
from tags.models import Tag


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, related_name='recipes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes'
    )
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to='recipes')
    text = models.TextField()
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Время приготовления (в минутах)"
    )

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ('ingredient', 'recipe')

    def __str__(self):
        return f'{self.ingredient.name} в {self.recipe.title}'
