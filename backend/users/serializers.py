from rest_framework import serializers
from users.models import CustomUser, Follow
import base64
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from rest_framework.relations import SlugRelatedField

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)
    
class UserSerializer(BaseUserSerializer):
    avatar = Base64ImageField(required=True, allow_null=True)
    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'is_subscribed', 'avatar'
        )

    
class UserSingupSerializer(BaseUserCreateSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'password'
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


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = CustomUser
        fields = (
            'avatar',
        )

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class FollowSerializer(serializers.ModelSerializer):
    following = UserSerializer(required=False)

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

    #def validate_following(self, value):
       # """The validator for the 'following' field."""
       # if value == self.context['request'].user:
        #   raise serializers.ValidationError('You can not follow yourself.')
        #return value
    
    def to_representation(self, instance):
        return FollowGetSerializer(instance).data
    
class FollowGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = (
            'id', 'username', 'email', 'last_name', 'is_subscribed', 'avatar'
        )
        extra_kwargs = {
            'id': {'read_only': True, 'required': False},
            'username': {'read_only': True, 'required': False},
        } 