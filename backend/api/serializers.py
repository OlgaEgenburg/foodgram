import base64

from django.core.files.base import ContentFile

from rest_framework import serializers

from recipe.models import (Ingredient, Recipe, RecipeIngredient, RecipeUser,
                           ShoppingList, Tag)
from users import models as user_models
from users.models import Follow


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientPostSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(default=None,)
    id = serializers.CharField(source='ingredient', required=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def get_alternate_name(self, obj):
        return obj.recipe


class IngredientAmountSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(read_only=True, default=None)
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_name(self, obj):
        return obj.ingredient.name

    def get_id(self, obj):
        return obj.ingredient.id

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = user_models.User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')

        if Follow.objects.filter(user=request.user.id,
                                 following=obj.id):
            return True
        return False


class RecipeSafeSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    tags = TagSerializer(many=True)
    ingredients = IngredientAmountSerializer(many=True, source='recipe_ing')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'ingredients', 'tags', 'image',
                  'text', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')
        read_only_fields = ('author', 'is_favorited')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if RecipeUser.objects.filter(user=request.user.id,
                                     recipe=obj.id):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if ShoppingList.objects.filter(user=request.user.id,
                                       recipe=obj.id):
            return True
        return False


class RecipeUnSafeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(required=True, allow_null=False,
                                              many=True,
                                              queryset=Tag.objects.all())
    ingredients = IngredientPostSerializer(required=True, many=True,
                                           allow_null=False)
    image = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('name', 'ingredients', 'tags', 'image',
                  'text', 'cooking_time')
        extra_kwargs = {
            'ingredients': {'required': True, 'allow_empty': False},
            'tags': {'required': True, 'allow_empty': False},
        }

    def to_representation(self, instance):
        return RecipeSafeSerializer(instance, context=self.context).data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients:
            ingredient_id = ingredient_data['ingredient']
            amount = ingredient_data['amount']
            try:
                current_ingredient = Ingredient.objects.get(id=ingredient_id)
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError('Ingredient does not exist')
            RecipeIngredient.objects.create(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=amount
            )
        for tag in tags:
            current_tag = Tag.objects.get(name=tag)
            recipe.tags.add(current_tag)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)

        ingredients_data = validated_data.pop('ingredients', [])

        for ingredient in ingredients_data:
            current_ingredient = ingredient.pop('ingredient')
            amount = ingredient.get('amount')
            ingredient = Ingredient.objects.get(id=current_ingredient)
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=amount
            )
        instance.save()
        return instance

    def validate(self, data):
        ing_list = []
        tag_list = []
        if 'tags' not in self.initial_data:
            raise serializers.ValidationError('Tag is nessecery')
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError('Ingredients are nessecery')
        for tag in (self.initial_data['tags']):
            if tag in tag_list:
                raise serializers.ValidationError('Tag has already in list')
            tag_list.append(tag)
        if len(self.initial_data['tags']) == 0:
            raise serializers.ValidationError('Add tags')
        if len(self.initial_data['ingredients']) == 0:
            raise serializers.ValidationError('Add ingredients')
        for ingredient in self.initial_data['ingredients']:
            if not Ingredient.objects.filter(id=(ingredient['id'])):
                raise serializers.ValidationError(
                    'There is no ingredient in data')
            if (ingredient['id']) < 1:
                raise serializers.ValidationError(
                    'No permission added for a ingredient')
            if (ingredient['amount']) < 1:
                raise serializers.ValidationError('Not enough for cooking')
            if (ingredient['id']) in ing_list:
                raise serializers.ValidationError('Ingredient already in list')
            ing_list.append(ingredient['id'])
        return data


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
        model = RecipeUser
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_name(self, obj):
        return obj.recipe.name

    def get_image(self, obj):
        image = RecipeImageSerializer(instance=obj.recipe,
                                      context=self.context).data
        image_url = list(image.values())[0]
        return image_url

    def get_cooking_time(self, obj):
        return obj.recipe.cooking_time


class FavoritePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeUser
        fields = ('user', 'recipe',)
        extra_kwargs = {
            'user': {'read_only': True},
            'recipe': {'read_only': True},
        }

    def create(self, validated_data):
        user = validated_data.pop('user')
        recipe = validated_data.pop('recipe')

        if RecipeUser.objects.filter(user=user, recipe=recipe):
            raise serializers.ValidationError('You can add againg.')
        follow = RecipeUser.objects.create(user=user, recipe=recipe)
        return follow

    def to_representation(self, instance):
        return FavoriteSerializer(instance).data


class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe',)
        extra_kwargs = {
            'user': {'read_only': True},
            'recipe': {'read_only': True},
        }

    def to_representation(self, instance):
        return FavoriteSerializer(instance).data

    def create(self, validated_data):
        user = self.context['request'].user
        recipe = validated_data.pop('recipe')
        if ShoppingList.objects.filter(user=user, recipe=recipe):
            raise serializers.ValidationError('You cannot add again.')
        list = ShoppingList.objects.create(user=user, recipe=recipe)
        return list
