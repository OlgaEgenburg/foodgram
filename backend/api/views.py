from django.core.files.base import ContentFile
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.serializers import (FavoritePostSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeSafeSerializer,
                             RecipeUnSafeSerializer, ShoppingListSerializer,
                             TagSerializer, UserSerializer)
from recipe.filters import RecipeFilter
from recipe.models import (Ingredient, Recipe, RecipeIngredient, RecipeUser,
                           ShoppingList, Tag)
from users import models as user_models
from users.models import Follow, User
from users.serializers import (AvatarSerializer, FollowGetSerializer,
                               FollowSerializer)

from .pagination import CustomPagination
from .permissions import IsAdminOrAuthorOrReadOnly, IsAdminOrReadOnly


class UserViewSet(UserViewSet):
    queryset = user_models.User.objects.all()
    pagination_class = LimitOffsetPagination
    serializer_class = UserSerializer

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar',
            serializer_class=AvatarSerializer,
            permission_classes=[IsAuthenticated])
    def avatar(self, request):
        if not request.data:
            if self.request.method == 'PUT':
                return HttpResponse(status=400)
            user = get_object_or_404(User, email=request.user)
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
        return Response(UserSerializer(request.user,
                                       context={'request': self.request}).data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=self.request.user)
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = FollowGetSerializer(result_page,
                                         context={'request': self.request},
                                         many=True)
        return paginator.get_paginated_response(serializer.data)


def get_card(request):
    return ShoppingList.objects.get(user=request.user.id)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = RecipeFilter
    pagination_class = LimitOffsetPagination
    filterset_fields = ('author', 'tags')

    @action(detail=False, methods=['get'], url_path='download_shopping_cart',
            permission_classes=[IsAuthenticated])
    def shopping_card(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_lists__user=request.user).values(
            'ingredient__name').annotate(total_amount=models.Sum('amount'))
        product_lines = [
            f"{ingredient['ingredient__name']}: {ingredient['total_amount']}"
            for ingredient in ingredients
        ]

        product_list = '\n'.join(product_lines)
        file_content = ContentFile(product_list)
        response = HttpResponse(file_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="cart.txt"'
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

    @action(detail=False, methods=['get'],
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
        serializer.save(user=self.request.user, recipe=self.get_recipe())

    def destroy(self, request, *args, **kwargs):
        if not get_object_or_404(Recipe, id=self.kwargs.get('recipe_id')):
            return HttpResponse(status=404)
        recipe = RecipeUser.objects.filter(
            user=self.request.user,
            recipe=self.kwargs.get('recipe_id'))
        if not recipe.exists():
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        else:
            recipe.delete()
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ModelViewSet):
    search_fields = ('name',)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ['name', ]
    http_method_names = ['get']

    def get_paginated_response(self, data):
        return Response(data)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get', 'post', 'delete']

    def get_following(self, **kwargs):
        return get_object_or_404(user_models.User,
                                 id=self.kwargs.get('user_id'))

    def retrieve(self, request, pk=None):
        user = user_models.User.objects.filter(id=self.get_following())
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
        if not get_object_or_404(User, id=self.kwargs.get('user_id')):
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        user = Follow.objects.filter(user=self.request.user,
                                     following=self.kwargs.get('user_id'))
        if not user.exists():
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        else:
            user.delete()
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)

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
    http_method_names = ['get']

    def get_queryset(self, **kwargs):
        data = self.queryset.filter(user=self.request.user)
        return data

    def retrieve(self, request, pk=None):
        queryset = Follow.objects.all()
        user = get_object_or_404(queryset, user=self.request.user)
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
        recipe = self.get_recipe()
        serializer.save(user=self.request.user, recipe=recipe)

    def destroy(self, request, *args, **kwargs):
        if not get_object_or_404(Recipe, id=self.kwargs.get('recipe_id')):
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        added_item = ShoppingList.objects.filter(
            user=self.request.user,
            recipe=self.kwargs.get('recipe_id'))
        if not added_item.exists():
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        else:
            added_item.delete()
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)
