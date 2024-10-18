import random

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (CHARACTERS, LINK_LENGTH, MAX_LENGTH_MEASUREMENT,
                        MAX_LENGTH_NAME, MAX_LENGTH_NAME_ING, MAX_LENGTH_SHORT)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField('Название', max_length=MAX_LENGTH_SHORT)
    slug = models.SlugField(
        'Идентификатор', max_length=MAX_LENGTH_SHORT, unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название игридиента',
                            max_length=MAX_LENGTH_NAME_ING, unique=True)
    measurement_unit = models.CharField('Название',
                                        max_length=MAX_LENGTH_MEASUREMENT)
  
    class Meta:
        verbose_name = 'Игредиент'
        verbose_name_plural = 'Игредиенты'

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe_id = models.ForeignKey(
        'Recipe',
        null=False,
        on_delete=models.CASCADE,
    )
    tag_id = models.ForeignKey(
        Tag,
        null=False,
        on_delete=models.CASCADE,
    )


class RecipeIngridient(models.Model):
    recipe_id = models.ForeignKey(
        'Recipe',
        null=False,
        on_delete=models.CASCADE,
        related_name='recipe_ing'
    )
    ingridient_id = models.ForeignKey(
        Ingredient,
        null=False,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.SmallIntegerField()

    class Meta:
        verbose_name = 'Рецепт-игредиент'
        verbose_name_plural = 'Рецепты-игредиенты'

    def __str__(self): 

        return self.recipe_id


class RecipeUser(models.Model):
    recipe_id = models.ForeignKey(
        'Recipe',
        null=False,
        on_delete=models.CASCADE,
        related_name='favorite'
    )
    user_id = models.ForeignKey(
        User,
        null=False,
        on_delete=models.CASCADE,
        related_name='favorite'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self): 

        return self.recipe_id


class ShoppingList(models.Model):
    recipe_id = models.ForeignKey(
        'Recipe',
        null=False,
        on_delete=models.CASCADE,
        related_name='shopping_lists'
    )
    user_id = models.ForeignKey(
        User,
        null=False,
        on_delete=models.CASCADE,
        related_name='shopping_lists'
    )

    def __str__(self): 

        return self.recipe_id
    
    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

class Recipe(models.Model):
    name = models.CharField('Название блюда',
                            max_length=MAX_LENGTH_NAME)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор', related_name='%(class)s_author'
    )
    tags = models.ManyToManyField(
        Tag,
        through=RecipeTag,
        verbose_name='Тэги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through=RecipeIngridient,
        verbose_name='Ингридиенты',
        related_name='recipes'
    )
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)
    image = models.ImageField('Фото', upload_to='recipe_images', blank=True,)
    text = models.TextField('Описание')
    cooking_time = models.SmallIntegerField('Время приготовления',
                                            validators=[MinValueValidator(1)])
    short_link = models.CharField(max_length=4, unique=True,
                                  blank=True, null=True)
    
    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.short_link:
            self.short_link = self.generate_short_link()
        super().save(*args, **kwargs)

    def generate_short_link(self):
        existing_links = set(Recipe.objects.values_list('short_link',
                                                        flat=True))
        while True:
            short_link = ''.join(random.choices(CHARACTERS, k=LINK_LENGTH))
            if short_link not in existing_links:
                break
        return short_link
