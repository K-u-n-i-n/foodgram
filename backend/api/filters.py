import django_filters

from recipes.models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        conjoined=False
    )
    is_favorited = django_filters.BooleanFilter(method='filter_is_favorited')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(favorited_by__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited']
