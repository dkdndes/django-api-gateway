from django.db import models
from django.contrib.auth.models import User


class CatBreed(models.Model):
    """Model to store cat breed information from TheCatAPI"""
    breed_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    temperament = models.CharField(max_length=255, blank=True, null=True)
    origin = models.CharField(max_length=100, blank=True, null=True)
    life_span = models.CharField(max_length=50, blank=True, null=True)
    wikipedia_url = models.URLField(blank=True, null=True)
    weight_imperial = models.CharField(max_length=50, blank=True, null=True)
    weight_metric = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CatImage(models.Model):
    """Model to store cat image information from TheCatAPI"""
    image_id = models.CharField(max_length=50, unique=True)
    url = models.URLField()
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    breeds = models.ManyToManyField(CatBreed, blank=True, related_name='images')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.image_id


class CatFavorite(models.Model):
    """Model to store user's favorite cat images"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cat_favorites')
    image = models.ForeignKey(CatImage, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'image')

    def __str__(self):
        return f"{self.user.username} - {self.image.image_id}"
