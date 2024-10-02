
import base64
from rest_framework import serializers
from recipe.models import Ingredient, Tag, Recipe, RecipeIngridient, RecipeTag
from users.serializers import UserSerializer
from django.core.files.base import ContentFile


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngridientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')

class IngridientAmountSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(read_only=True, default=None)
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngridientPostSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(default=None)
    id = serializers.CharField(source='ingridient_id')

    class Meta:
        model = RecipeIngridient
        fields = ('id', 'amount')

    def get_alternate_name(self, obj):
        return obj.recipe_id

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSafeSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    tags = TagSerializer(many=True)
    ingredients = IngridientAmountSerializer(many=True,)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)


class RecipeUnSafeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(required=True,allow_null=False, many=True, queryset=Tag.objects.all())
    ingredients = IngridientPostSerializer(required=True, many=True, allow_null=False)
    image = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('name', 'ingredients', 'tags', 'image', 'text', 'cooking_time')
        extra_kwargs = {
            'ingredients': {'required': True},
            'tags': {'required': True}
            } 

    def to_representation(self, instance):
        return RecipeSafeSerializer(instance).data
    
    def create(self, validated_data):
        print(validated_data)
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:

            ing = int(list(ingredient.values())[0])
            current_ingredient = Ingredient.objects.get(id=ing)
            RecipeIngridient.objects.create(
                ingridient_id=current_ingredient, recipe_id=recipe, amount=3
                )
        for tag in tags:
            print(tag)
            current_tag = Tag.objects.get(name=tag)
            print(current_tag)
            RecipeTag.objects.create(
                 tag_id=current_tag, recipe_id=recipe
                )
        return recipe
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        ingredients_data = validated_data.pop('ingredients')
        lst = []
        for ingredient in ingredients_data:
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient
                )
            lst.append(current_ingredient)
        instance.ingredients.set(lst)
        instance.ingredients.amount = 1
        instance.save()
        return instance

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

