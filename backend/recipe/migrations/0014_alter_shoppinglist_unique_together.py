# Generated by Django 4.2.16 on 2024-10-07 15:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0013_shoppinglist'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='shoppinglist',
            unique_together=set(),
        ),
    ]
