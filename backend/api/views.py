from rest_framework import filters, viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
#from rest_framework import generics
from django.http import HttpResponse
#from wsgiref.util import FileWrapper
from api.serializers import (FavoriteSerializer, TagSerializer,
                             IngridientSerializer, RecipeSafeSerializer, UserSerializer, RecipeUnSafeSerializer, FavoritePostSerializer, ShoppingListSerializer)
from users.serializers import FollowSerializer, FollowGetSerializer
from recipe.models import Ingredient, Tag, Recipe, RecipeUser, ShoppingList
from .permissions import IsAdminOrAuthorOrReadOnly, IsAdminOrReadOnly
from recipe.filters import RecipeFilter
from users.models import CustomUser, Follow
from users.serializers import AvatarSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
#from django.core.exceptions import ValidationError
from users import models as user_models
from djoser.views import UserViewSet
from rest_framework.decorators import action
from django.core.files.base import ContentFile


class UserViewSet(UserViewSet):
    queryset = user_models.CustomUser.objects.all()
    pagination_class = LimitOffsetPagination
    serilizer_class = UserSerializer

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar', serializer_class=AvatarSerializer, permission_classes=[IsAuthenticated])
    def avatar(self, request):
        if not request.data:
            if self.request.method == 'PUT':
                return HttpResponse(status=400)
            user = get_object_or_404(CustomUser, email=request.user)
            user.avatar.delete()
            user.save
            return HttpResponse(status=204)
        serializer = AvatarSerializer(request.user, data=request.data,)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False,
            methods=['GET'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        return Response(UserSerializer(request.user).data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['get',], url_path='subscriptions')
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=self.request.user)
        paginator = PageNumberPagination()
        page_size = 10
        paginator.page_size = page_size
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = FollowGetSerializer(result_page,
                                         context={'request': self.request},
                                         many=True)
        return paginator.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = RecipeFilter
    pagination_class = LimitOffsetPagination
    filterset_fields = ('author', 'tags') 

    @action(detail=False, methods=['get',], url_path='download_shopping_cart', permission_classes=[IsAuthenticated])
    def shopping_card(self, request):
        shopping_list = ShoppingList.objects.get(user_id=request.user.id)
        #product_list = "\n".join([f"{item.recipe_id} x {item.recipe_id}" for item in shopping_list])
        product_list = "hi"
        file_content = ContentFile(product_list)
        response = HttpResponse(file_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSafeSerializer
        return RecipeUnSafeSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request 
        return context
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user, )

    @action(detail=False, methods=['get',],
            url_path=r'(?P<recipe_id>\d+)/get-link')
    def get_link(self, request, **kwargs):
        recipe = Recipe.objects.filter(id=self.kwargs.get('recipe_id')).first()
        if recipe is None:
            return Response('Recipe not found', status=404)
        short_link = f'https://mysite.com/{recipe.short_link}'
        return Response({'short-link': short_link})


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

    def destroy(self, request, *args, **kwargs):
        if not get_object_or_404(Recipe, id=self.kwargs.get('recipe_id')):
            return HttpResponse(status=404)
        recipe = RecipeUser.objects.filter(user_id=self.request.user, recipe_id=self.kwargs.get('recipe_id'))
        if not recipe.exists():
            return HttpResponse(status=400)
        else:
            recipe.delete()
            return HttpResponse(status=204)


class IngridientViewSet(viewsets.ModelViewSet):
    search_fields = ('name',)
    queryset = Ingredient.objects.all()
    serializer_class = IngridientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ['name',]
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
        return get_object_or_404(user_models.CustomUser,
                                 id=self.kwargs.get('user_id'))
    
    def retrieve(self, request, pk=None):
        user = user_models.CustomUser.objects.filter(id=self.get_following())
        serializer = FollowSerializer(user,
                                      context=self.get_serializer_context())
        return Response(serializer.data)

    def perform_create(self, serializer,):
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user, following=self.get_following())
    
    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return FollowGetSerializer
        return FollowSerializer
    
    def destroy(self, request, *args, **kwargs):
        if not get_object_or_404(CustomUser, id=self.kwargs.get('user_id')):
            return HttpResponse(status=404)
        user = Follow.objects.filter(user=self.request.user,
                                     following=self.kwargs.get('user_id'))
        if not user.exists():
            return HttpResponse(status=400)
        else:
            user.delete()
            return HttpResponse(status=204)

    def get_serializer_context(self):
        return {
           'request': self.request,
           'format': self.format_kwarg,
           'view': self
        }


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowGetSerializer
    permission_classes = (AllowAny, )
    http_method_names = ['get',]

    def get_queryset(self, **kwargs):
        data = self.queryset.filter(user_id=self.request.user)
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
        return recipe

    def retrieve(self, request, pk=None):
        queryset = self.get_recipe()
        return queryset

    def perform_create(self, serializer):

        serializer.save(user_id=self.request.user, recipe_id=self.get_recipe())

    def destroy(self, request, *args, **kwargs):
        if not get_object_or_404(Recipe, id=self.kwargs.get('recipe_id')):
            return HttpResponse(status=404)
        added_item = ShoppingList.objects.filter(user_id=self.request.user,
                                                 recipe_id=self.kwargs.get('recipe_id'))
        if not added_item.exists():
            return HttpResponse(status=400)
        else:
            added_item.delete()
            return HttpResponse(status=204)
