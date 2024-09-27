from django.db import models
from django.contrib.auth import get_user_model
from .constants import (MAX_LENGTH_NAME, MAX_LENGTH_SHORT, MAX_LENGTH_NAME_ING, MAX_LENGTH_MEASUREMENT) 

User = get_user_model()


class Tag(models.Model):
    name = models.CharField('Название', max_length=MAX_LENGTH_SHORT)
    slug = models.SlugField(
        'Идентификатор', max_length=MAX_LENGTH_SHORT, unique=True)


class Ingridient(models.Model):
    name = models.CharField('Название игридиента', max_length=MAX_LENGTH_NAME_ING)
    measurement_unit = models.CharField('Название', max_length=MAX_LENGTH_MEASUREMENT)  


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
    )
    ingridient_id = models.ForeignKey(
        Ingridient,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    amount = models.SmallIntegerField()

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
    ingridients = models.ManyToManyField(
        Ingridient,
        through=RecipeIngridient,
        blank=False,
        verbose_name='Ингридиенты',
    )
    is_favorited = models.BooleanField()
    is_in_shopping_cart = models.BooleanField()
    image = models.ImageField('Фото', upload_to='recipe_images', blank=True)
    text = models.TextField()
    cooking_time = models.SmallIntegerField('Время приготовления')

    REQUIRED_FIELDS = ('ingridients', 'tags', 'name', 'text', 'cooking_time')