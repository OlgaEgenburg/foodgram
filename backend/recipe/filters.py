import django_filters
from django_filters import CharFilter, FilterSet, rest_framework

from recipe.models import Recipe

from .models import Ingredient, Tag


class RecipeFilter(rest_framework.FilterSet):
    author = rest_framework.CharFilter(field_name='author__id')
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='filter_shopping_cart'
    )
    is_favorited = rest_framework.BooleanFilter(method='filter_is_favorite')

    class Meta:
        fields = ('author', 'tags')
        model = Recipe

    def filter_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            return queryset.filter(
                shopping_lists__user_id=user
            ) if value else queryset.exclude(shopping_lists__user_id=user)
        return queryset

    def filter_is_favorite(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            return queryset.filter(
                favorite__user_id=user
            ) if value else queryset.exclude(favorite__user_id=user)
        return queryset


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
