from django.urls import include, path

from rest_framework import routers

from .views import (FavoriteViewSet, FollowViewSet, IngredientViewSet,
                    RecipeViewSet, ShoppingListViewSet, TagViewSet,
                    UserViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='genres')


urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('users/<int:user_id>/subscribe/', FollowViewSet.as_view({
        'get': 'retrieve',
        'post': 'create',
        'put': 'update',
        'delete': 'destroy'
    })),
    path('recipes/<int:recipe_id>/favorite/', FavoriteViewSet.as_view({
        'get': 'retrieve',
        'post': 'create',
        'put': 'update',
        'delete': 'destroy'
    })),
    path(
        'recipes/<int:recipe_id>/shopping_cart/', ShoppingListViewSet.as_view({
            'get': 'retrieve',
            'post': 'create',
            'put': 'update',
            'delete': 'destroy'})),
    path('auth/', include('djoser.urls.authtoken'))
]
