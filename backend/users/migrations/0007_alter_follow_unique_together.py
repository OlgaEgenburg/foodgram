# Generated by Django 4.2.16 on 2024-10-08 02:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_follow_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together=set(),
        ),
    ]
