# Generated by Django 4.2.16 on 2024-10-17 04:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0023_shoppinglist_items_alter_recipe_text_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shoppinglist',
            name='items',
        ),
    ]
