from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for our API views
router = DefaultRouter()
router.register(r"breeds", views.CatBreedViewSet)
router.register(r"images", views.CatImageViewSet)
router.register(r"favorites", views.CatFavoriteViewSet, basename="favorites")

app_name = "cat_api"

# URL patterns for the Cat API
urlpatterns = [
    # API endpoints
    path("api/", include(router.urls)),
    # Web interface
    path("", views.cat_home, name="home"),
    path("breeds/", views.cat_breeds, name="breeds_list"),
    path("breeds/<str:breed_id>/", views.cat_breed_detail, name="breed_detail"),
    path("favorites/", views.cat_favorites, name="favorites"),
    path("demo/", views.cat_demo, name="cat_demo"),
    # HTMX endpoints
    path("htmx/random-cats/", views.random_cats, name="random_cats"),
    path("htmx/breed-images/", views.breed_images, name="breed_images"),
    path(
        "htmx/breed-detail/<str:breed_id>/",
        views.breed_detail_api,
        name="breed_detail_api",
    ),
    path("htmx/add-favorite/", views.add_favorite, name="add_favorite"),
    path("htmx/remove-favorite/", views.remove_favorite, name="remove_favorite"),
]
