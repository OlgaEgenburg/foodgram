from rest_framework import filters, viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from api.serializers import (FavoriteSerializer, TagSerializer,
                             IngridientSerializer, RecipeSafeSerializer, RecipeUnSafeSerializer, FavoritePostSerializer)
from users.serializers import FollowSerializer, FollowGetSerializer
from recipe.models import Ingredient, Tag, Recipe, RecipeUser
from .permissions import IsAdminOrAuthorOrReadOnly, IsAdminOrReadOnly
from recipe.filters import RecipeFilter
from users.models import CustomUser, Follow
from users.serializers import AvatarSerializer
from .mixin import AllowPUTAsCreateMixin, AllowPUTAsCreateMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSafeSerializer
        return RecipeUnSafeSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user, )


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
    queryset = Recipe.objects.all()
    http_method_names = ['post', 'delete']
    serializer_class = FavoriteSerializer

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return FavoriteSerializer
        return FavoritePostSerializer

    def get_recipe(self):
        return get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
    
    def retrieve(self, request, pk=None):
        queryset = self.get_recipe()
        return queryset

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user, recipe_id=self.get_recipe())



class IngridientViewSet(viewsets.ModelViewSet):
    search_fields = ('name',)
    queryset = Ingredient.objects.all()
    serializer_class = IngridientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ['get']

    def get_paginated_response(self, data):
        return Response(data)
    
class AvatarViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = AvatarSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    http_method_names = ['put', 'delete']
    lookup_fields = ['avatar', ]
    
    def get_object(self):
        user = get_object_or_404(CustomUser, id=self.request.user.id)
        return user


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self, **kwargs):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return FollowGetSerializer
        return FollowSerializer
    
class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = FollowGetSerializer
    permission_classes = (AllowAny, )
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)
    http_method_names = ['get',]

    def get_queryset(self, **kwargs):
        return self.queryset.filter(user=self.request.user)