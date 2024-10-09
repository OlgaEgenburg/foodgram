from rest_framework import filters, viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import generics
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from api.serializers import (FavoriteSerializer, TagSerializer,
                             IngridientSerializer, RecipeSafeSerializer, ShortLinkSerializer, RecipeUnSafeSerializer, FavoritePostSerializer, ShoppingListSerializer)
from users.serializers import FollowSerializer, FollowGetSerializer
from recipe.models import Ingredient, Tag, Recipe, RecipeUser, ShoppingList
from .permissions import IsAdminOrAuthorOrReadOnly, IsAdminOrReadOnly
from recipe.filters import RecipeFilter
from users.models import CustomUser, Follow
from users.serializers import AvatarSerializer
from .mixin import AllowPUTAsCreateMixin, AllowPUTAsCreateMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import LimitOffsetPagination
from django.core.exceptions import ValidationError

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = RecipeFilter
    pagination_class = LimitOffsetPagination
    filterset_fields = ('author', 'tags') 

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSafeSerializer
        return RecipeUnSafeSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user, )


class TagViewSet(viewsets.ModelViewSet):
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
    permission_classes = (IsAuthenticated, )
    http_method_names = ['put', 'delete']
    lookup_fields = ['avatar', ]
    
    def get_object(self):
        user = get_object_or_404(CustomUser, id=self.request.user.id)
        return user


class FollowViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get', 'post', 'delete']

    def get_following(self, **kwargs):
        return get_object_or_404(CustomUser, id=self.kwargs.get('user_id'))
    
    def retrieve(self, request, pk=None):
        #queryset = self.get_following()
        #return queryset
        queryset = CustomUser.objects.all()
        user = get_object_or_404(queryset, id=self.kwargs.get('user_id'))
        serializer = FollowGetSerializer(user)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, following=self.get_following())
    
    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return FollowGetSerializer
        return FollowSerializer
    
class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowGetSerializer
    permission_classes = (AllowAny, )
    http_method_names = ['get',]

    def get_queryset(self, **kwargs):
        print("hi")
        data = self.queryset.filter(user_id=self.request.user)
        print(data)
        return data
    
    def retrieve(self, request, pk=None):
        queryset = Follow.objects.all()
        user = get_object_or_404(queryset, user_id=self.request.user)
        serializer = FollowGetSerializer(user)
        return Response(serializer.data)
    

class ShoppingListViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticated, )
    http_method_names = ['post', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return FavoriteSerializer
        return ShoppingListSerializer

    def get_recipe(self):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        print(recipe)
        if ShoppingList.objects.filter(recipe_id__name=recipe):
            raise ValidationError("Recipe already in list")
        else:
            return recipe
    
    def retrieve(self, request, pk=None):
        queryset = self.get_recipe()
        return queryset

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user, recipe_id=self.get_recipe())


class ShortLinkViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = ShortLinkSerializer
    permission_classes = (AllowAny, )
    http_method_names = ['get',]

    def get_queryset(self, **kwargs):
        return self.queryset.filter(user=self.request.user)


class DownloadCartAPIView(generics.ListAPIView):
    def get(self, request, id, format=None):
        queryset = ShoppingList.objects.get(user_id=self.request.user)
        print(queryset)
        file_handle = queryset.file.path
        document = open(file_handle, 'rb')
        response = HttpResponse(FileWrapper(document), content_type='application/msword')
        response['Content-Disposition'] = 'attachment; filename="%s"' % queryset.file.name
        return response