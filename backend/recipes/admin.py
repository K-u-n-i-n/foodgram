from django.contrib import admin

from .models import (
    CustomUser,
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag
)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'password',
        'avatar'
    )
    list_editable = (
        'username',
        'first_name',
        'last_name',
        'password',
        'avatar'
    )
    search_fields = (
        'email',
        'username'
    )
    list_filter = ('username',)
    empty_value_display = 'Не задано'
    list_per_page = 10


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )
    list_editable = ('author',)
    search_fields = (
        'user',
        'author'
    )
    list_filter = ('user', 'author')
    list_per_page = 10


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    list_editable = ('measurement_unit',)
    search_fields = ('name',)
    # list_filter = ('name',)
    list_per_page = 20


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug'
    )
    list_editable = ('slug',)
    search_fields = ('name',)
    list_filter = ('name',)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1
    fields = ('ingredient', 'amount')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'image',
        'short_text',
        'cooking_time',
        'get_favorites_count'
    )
    autocomplete_fields = (
        'ingredients',
        'tags',
        'author'
    )
    list_editable = (
        'image',
        'cooking_time'
    )
    search_fields = (
        'name',
        'author__username'
    )
    list_filter = ('tags',)  # Не работает, разобраться
    empty_value_display = 'Не задано'
    list_per_page = 10
    inlines = (IngredientInRecipeInline,)

    @admin.display(description='Текст')
    def short_text(self, obj):
        return obj.text if len(obj.text) < 100 else obj.text[:100] + '...'

    def get_favorites_count(self, obj):
        return obj.favorited_by.count()

    get_favorites_count.short_description = 'Количество добавлений в избранное'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')
