from django.db import models
from django.contrib.auth import get_user_model
from .constants import (MAX_LENGTH_NAME, MAX_LENGTH_SHORT, MAX_LENGTH_NAME_ING, MAX_LENGTH_MEASUREMENT, CHARACTERS, LINK_LENGTH) 
from django.core.validators import MinValueValidator
import random

User = get_user_model()


class Tag(models.Model):
    name = models.CharField('Название', max_length=MAX_LENGTH_SHORT)
    slug = models.SlugField(
        'Идентификатор', max_length=MAX_LENGTH_SHORT, unique=True)
    
    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название игридиента',
                            max_length=MAX_LENGTH_NAME_ING)
    measurement_unit = models.CharField('Название',
                                        max_length=MAX_LENGTH_MEASUREMENT)  

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe_id = models.ForeignKey(
        'Recipe',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    tag_id = models.ForeignKey(
        Tag,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )


class RecipeIngridient(models.Model):
    recipe_id = models.ForeignKey(
        'Recipe',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='recipe_ing'
    )
    ingridient_id = models.ForeignKey(
        Ingredient,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.SmallIntegerField()


class RecipeUser(models.Model):
    recipe_id = models.ForeignKey(
        'Recipe',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='favorite'
    )
    user_id = models.ForeignKey(
        User,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='favorite'
    )


class ShoppingList(models.Model):
    recipe_id = models.ForeignKey(
        'Recipe',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='shopping_lists'
    )
    user_id = models.ForeignKey(
        User,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='shopping_lists'
    )


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
        blank=False,
        verbose_name='Тэги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through=RecipeIngridient,
        blank=False,
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
