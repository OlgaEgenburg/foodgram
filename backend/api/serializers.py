
import base64
from rest_framework import serializers
from recipe.models import Ingredient, Tag, Recipe, RecipeIngridient, RecipeTag, RecipeUser
from users.serializers import UserSerializer
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngridientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')




class IngridientPostSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(default=None)
    id = serializers.CharField(source='ingridient_id')

    class Meta:
        model = RecipeIngridient
        fields = ('id', 'amount')

    def get_alternate_name(self, obj):
        return obj.recipe_id
    
class IngridientAmountSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(read_only=True, default=None)
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngridient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_name(self, obj):
        return obj.ingridient_id.name
    
    def get_id(self, obj):
        return obj.ingridient_id.id
    
    def get_measurement_unit(self, obj):
        return obj.ingridient_id.measurement_unit



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
    ingredients = IngridientAmountSerializer(many=True, source='recipe_ing')

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)


class RecipeUnSafeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(required=True, allow_null=False, many=True, queryset=Tag.objects.all())
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
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:

            ing = int(list(ingredient.values())[0])
            amount = int(list(ingredient.values())[1])
            current_ingredient = Ingredient.objects.get(id=ing)
            RecipeIngridient.objects.create(
                ingridient_id=current_ingredient, recipe_id=recipe, amount=amount
                )
        for tag in tags:
            current_tag = Tag.objects.get(name=tag)
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
    



class RecipeImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('image',)

class FavoriteSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    cooking_time = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_name(self, obj):
        return obj.recipe_id.name
    
    def get_image(self, obj):
        image = RecipeImageSerializer(instance=obj.recipe_id, context=self.context).data
        image_url = list(image.values())[0]
        return image_url
    
    def get_cooking_time(self, obj):
        return obj.recipe_id.cooking_time



class FavoritePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeUser
        fields = ('user_id', 'recipe_id',)
        extra_kwargs = {
            'user_id': {'read_only': True},
            'recipe_id': {'read_only': True},
        }

    def to_representation(self, instance):
        return FavoriteSerializer(instance).data
    


