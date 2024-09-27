from rest_framework import viewsets

from api.serializers import (RecipeSafeSerializer, TagSerializer,
                             IngridientSerializer)
from recipe.models import Ingridient, Tag, Recipe


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']


class TagViewSet(viewsets.ModelViewSet):
    search_fields = ('name',)
    lookup_field = 'slug'
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngridientViewSet(viewsets.ModelViewSet):
    search_fields = ('name',)
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
