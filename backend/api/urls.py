from django.urls import include, path
from rest_framework import routers

from .views import (IngridientViewSet, TagViewSet, RecipeViewSet, FavoriteViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngridientViewSet, basename='genres')
router_v1.register('recipes/download_shopping_cart/', IngridientViewSet, basename='download_cart')
router_v1.register('users/subscriptions/', IngridientViewSet, basename='subscription')
router_v1.register(r'recipes/(?P<recipe_id>\d+)/favorite',FavoriteViewSet, basename='favorite')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))

]
