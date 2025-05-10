from django.contrib import admin
from .models import CatBreed, CatImage, CatFavorite

@admin.register(CatBreed)
class CatBreedAdmin(admin.ModelAdmin):
    list_display = ('name', 'breed_id', 'origin', 'created_at')
    list_filter = ('origin', 'created_at')
    search_fields = ('name', 'breed_id', 'description', 'temperament', 'origin')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

@admin.register(CatImage)
class CatImageAdmin(admin.ModelAdmin):
    list_display = ('image_id', 'url', 'width', 'height', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('image_id', 'url')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    filter_horizontal = ('breeds',)

@admin.register(CatFavorite)
class CatFavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username', 'image__image_id')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
