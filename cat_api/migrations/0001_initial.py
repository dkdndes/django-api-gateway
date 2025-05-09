# Generated by Django 5.2.1 on 2025-05-10 13:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CatBreed",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("breed_id", models.CharField(max_length=50, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "temperament",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("origin", models.CharField(blank=True, max_length=100, null=True)),
                ("life_span", models.CharField(blank=True, max_length=50, null=True)),
                ("wikipedia_url", models.URLField(blank=True, null=True)),
                (
                    "weight_imperial",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "weight_metric",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="CatImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("image_id", models.CharField(max_length=50, unique=True)),
                ("url", models.URLField()),
                ("width", models.IntegerField(blank=True, null=True)),
                ("height", models.IntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "breeds",
                    models.ManyToManyField(
                        blank=True, related_name="images", to="cat_api.catbreed"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CatFavorite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cat_favorites",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorites",
                        to="cat_api.catimage",
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "image")},
            },
        ),
    ]
