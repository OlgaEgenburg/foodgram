from django.urls import include, path
from rest_framework import routers
from users.views import AvatarViewSet
from .views import (IngridientViewSet, TagViewSet, RecipeViewSet, FavoriteViewSet, FollowViewSet, SubscriptionViewSet, ShortLinkViewSet, ShoppingListViewSet)
from . import views

router_v1 = routers.DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngridientViewSet, basename='genres')
#router_v1.register('recipes/download_shopping_cart', DownloadCartViewSet, basename='download_cart')
router_v1.register(r'users/(?P<user_id>\d+)/subscribe', FollowViewSet, basename='subscription')
#router_v1.register('users/subscribtion', SubscriptionViewSet, basename='mysubscription')
#router_v1.register('users/me/avatar', AvatarViewSet, basename='avatar')
router_v1.register(r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet, basename='favorite')
router_v1.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart', ShoppingListViewSet, basename='shopping-list')
router_v1.register(r'recipes/(?P<recipe_id>\d+)/get-link', ShortLinkViewSet, basename='short-link')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('recipes/download_shopping_cart', views.DownloadCartAPIView.as_view(), name='download_cart'),
    path('users/subscribtion', views.SubscriptionViewSet.as_view({'get': 'list'}), name='mysubscription'),
    
    #path('users/me/avatar/', views.AvatarViewSet.as_view({'put': 'update',
                                                        # 'get': 'retrieve', 
                                                         # 'delete': 'destroy'})),
    path('auth/', include('djoser.urls.authtoken'))
]
