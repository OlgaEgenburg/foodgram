# Generated by Django 4.2.16 on 2024-10-17 04:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipe', '0022_alter_recipe_short_link_alter_shoppinglist_recipe_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppinglist',
            name='items',
            field=models.JSONField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recipe',
            name='text',
            field=models.TextField(verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='recipeuser',
            name='recipe_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to='recipe.recipe'),
        ),
        migrations.AlterField(
            model_name='recipeuser',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to=settings.AUTH_USER_MODEL),
        ),
    ]
