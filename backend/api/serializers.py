from rest_framework import serializers
from recipe.models import Ingridient, Tag, Recipe
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngridientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingridient
        fields = ('id', 'name', 'measurement_unit')


class IngridientUnsafeSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(read_only=True, default=None)
    class Meta:
        model = Ingridient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSafeSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    tags = TagSerializer(many=True)
    ingredients = IngridientSerializer(many=True)
    class Meta:
        model = Recipe
        fields = '__all__'

class RecipeUnSafeSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    ingredients = IngridientSerializer(many=True)
    class Meta:
        model = Recipe
        fields = '__all__'