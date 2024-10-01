from rest_framework import serializers
from users.models import CustomUser
from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer

class UserSerializer(BaseUserSerializer):
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