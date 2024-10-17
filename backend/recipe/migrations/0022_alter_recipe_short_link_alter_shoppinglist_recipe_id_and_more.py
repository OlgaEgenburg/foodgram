# Generated by Django 4.2.16 on 2024-10-17 00:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipe', '0021_recipe_short_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='short_link',
            field=models.CharField(blank=True, max_length=4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='shoppinglist',
            name='recipe_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_lists', to='recipe.recipe'),
        ),
        migrations.AlterField(
            model_name='shoppinglist',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_lists', to=settings.AUTH_USER_MODEL),
        ),
    ]