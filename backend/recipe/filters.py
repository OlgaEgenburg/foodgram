from django_filters import rest_framework

from recipe.models import Recipe


class RecipeFilter(rest_framework.FilterSet):
    author = rest_framework.CharFilter(field_name='author__username')
    tags = rest_framework.CharFilter(field_name='tags__slug')
    is_in_shopping_cart = rest_framework.CharFilter(field_name='is_in_shopping_cart')
    is_favorited = rest_framework.CharFilter(field_name='is_favorited')

    class Meta:
        fields = ('author', 'tags', 'is_in_shopping_cart', 'is_favorited')
        model = Recipe
