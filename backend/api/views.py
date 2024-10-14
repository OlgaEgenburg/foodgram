from rest_framework import filters, viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import generics
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from api.serializers import (FavoriteSerializer, TagSerializer,
                             IngridientSerializer, RecipeSafeSerializer, ShortLinkSerializer, UserSerializer, RecipeUnSafeSerializer, FavoritePostSerializer, ShoppingListSerializer)
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
from users import models as user_models
from users.serializers import  UserSingupSerializer
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination


class UserViewSet(UserViewSet):
    queryset = user_models.CustomUser.objects.all()
    pagination_class = LimitOffsetPagination
    serilizer_class = UserSerializer
    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserSerializer
        return UserSingupSerializer
    
    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar', serializer_class=AvatarSerializer, permission_classes=[IsAuthenticated])
    def avatar(self, request):
        if not request.data:
            if self.request.method == 'PUT':
                return HttpResponse(status=400)
            user = get_object_or_404(CustomUser, email=request.user)
            user.avatar.delete()
            user.save
            return HttpResponse(status=204)
        #if request.data == "":
            #return HttpResponse(status=400)
        serializer = AvatarSerializer(request.user,
                                            data=request.data,)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(request.data)
        return Response(serializer.data)

    @action(detail=False,
            methods=['GET'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        return Response(UserSerializer(request.user).data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['get',], url_path='subscriptions', pagination_class = LimitOffsetPagination)
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=self.request.user)
        paginator = PageNumberPagination()
        #limit = self.request.query_params.get('limit')
        page_size = 10
        paginator.page_size = page_size
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = FollowGetSerializer(result_page, context={'request': self.request}, many=True)

        #return Response(serializer.data)
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
        queryset = ShoppingList.objects.get(user_id=self.request.user)
        print(queryset)
        file_handle = queryset.file.path
        document = open(file_handle, 'rb')
        response = HttpResponse(FileWrapper(document), content_type='application/msword')
        response['Content-Disposition'] = 'attachment; filename="%s"' % queryset.file.name
        return response

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSafeSerializer
        return RecipeUnSafeSerializer
    
    def get_serializer_context(self):
        # Получаем контекст от родительского класса и добавляем текущий запрос
        context = super().get_serializer_context()
        context['request'] = self.request 
        print(context) # добавляем текущий запрос
        return context
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user, )

    @action(detail=False, methods=['get',], url_path='shopping_cart', permission_classes=[IsAuthenticated])
    def add_shopping_card(self, request):
        
    


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
        print(self.request.user)
        print(self.kwargs.get('recipe_id'))
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
        return get_object_or_404(user_models.CustomUser, id=self.kwargs.get('user_id'))
    
    def retrieve(self, request, pk=None):
        user = user_models.CustomUser.objects.filter(id=self.get_following())
        serializer = FollowSerializer(user, context=self.get_serializer_context())
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
        user = Follow.objects.filter(user=self.request.user, following=self.kwargs.get('user_id'))
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
        return recipe
    
    def retrieve(self, request, pk=None):
        queryset = self.get_recipe()
        return queryset

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        #if ShoppingList.objects.filter(recipe_id__name=recipe):
            #return Response("Item already exists", status.HTTP_400_BAD_REQUEST)
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