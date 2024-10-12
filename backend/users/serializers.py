from rest_framework import serializers
from users.models import CustomUser, Follow
from users import models as user_models
import base64
from django.core.files.base import ContentFile
#from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from rest_framework.relations import SlugRelatedField
from djoser.serializers import  UserCreateSerializer
from api.serializers import RecipeSafeSerializer, FavoriteSerializer
from recipe.models import Recipe

    
class UserSingupSerializer(UserCreateSerializer):
    class Meta:
        model = user_models.CustomUser
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'password',
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    #def to_representation(self, instance):
        #return UserSerializer(instance).data

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'email', 'password'
        )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = user_models.CustomUser
        fields = (
            'avatar',
        )

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.id = validated_data.get('id', instance.id)
        instance.save()
        return instance
    
    #def delete(self, instance, *args, **kwargs):
        #instance.avatar.delete()
        #super(CustomUser, self).delete(*args, **kwargs)


class UserSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = user_models.CustomUser
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'is_subscribed', 'avatar'
        )



class FollowSerializer(serializers.ModelSerializer):
    #following = UserSerializer(required=False)

    class Meta:
        fields = ('user', 'following')
        model = Follow
        #validators = [
            #serializers.UniqueTogetherValidator(
                #queryset=Follow.objects.all(), fields=['user', 'following']
            #)
        #]
        #optional_fields = ['user', ]
        extra_kwargs = {
            'user': {'write_only': True, 'required': False},
            'following': { 'required': False},
        } 

    
    def create(self, validated_data):
        user = validated_data.pop('user')
        following = validated_data.pop('following')
        if user == following:
            raise serializers.ValidationError('You can not follow yourself.')
        if Follow.objects.filter(user=user, following=following):
            raise serializers.ValidationError('You can not follow againg.')
        follow = Follow.objects.create(user=user, following=following)
        return follow
    
    def to_representation(self, instance):
        return FollowGetSerializer(instance).data
    

class FollowRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


    
class FollowGetSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='following.email',)
    username = serializers.CharField(source='following.username',)
    last_name = serializers.CharField(source='following.last_name',)
    first_name = serializers.CharField(source='following.first_name',)
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(source='following.avatar')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'id', 'email', 'username', 'last_name', 'is_subscribed', 'avatar', 'first_name', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        if Follow.objects.filter(user=obj.user, following=obj.following):
            return True

    def get_recipes(self, obj):
        recipe = Recipe.objects.filter(author=obj.following)
        return FollowRecipeSerializer(recipe, many=True).data
    
    def get_recipes_count(self, obj):
        recipe = Recipe.objects.filter(author=obj.following)
        return recipe.count()


