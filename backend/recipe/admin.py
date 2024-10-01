from django.contrib import admin

from .models import Tag, Ingridient, Recipe

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name', 'author')
    list_filter = ('tags',)
    empty_value_display = '-пусто-'


class IngridientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = '-пусто-'

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingridient, IngridientAdmin)
admin.site.register(Tag, TagAdmin)