from django_filters import rest_framework
import django_filters
from .models import Tag
from recipe.models import Recipe


class RecipeFilter(rest_framework.FilterSet):
    author = rest_framework.CharFilter(field_name='author__id')
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_in_shopping_cart = rest_framework.BooleanFilter(field_name='is_in_shopping_cart')
    is_favorited = rest_framework.BooleanFilter(field_name='is_favorited')

    class Meta:
        fields = ('author', 'tags', 'is_in_shopping_cart', 'is_favorited')
        model = Recipe
