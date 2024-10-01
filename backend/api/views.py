from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from api.serializers import (FavoriteSerializer, TagSerializer,
                             IngridientSerializer, RecipeSafeSerializer, RecipeUnSafeSerializer)
from recipe.models import Ingridient, Tag, Recipe
from .permissions import IsAdminOrAuthorOrReadOnly, IsAdminOrReadOnly

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAdminOrAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSafeSerializer
        return RecipeUnSafeSerializer


class TagViewSet(viewsets.ModelViewSet):
    #search_fields = ('name',)
    #lookup_field = 'slug'
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    http_method_names = ['get']

    def get_paginated_response(self, data):
        return Response(data)



class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    http_method_names = ['post', 'delete']
    serializer_class = FavoriteSerializer

    def get_recipe(self):
        return get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, recipe=self.get_recipe())



class IngridientViewSet(viewsets.ModelViewSet):
    search_fields = ('name',)
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ['get']

    def get_paginated_response(self, data):
        return Response(data)
