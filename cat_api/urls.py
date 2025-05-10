from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for our API views
router = DefaultRouter()
router.register(r'breeds', views.CatBreedViewSet)
router.register(r'images', views.CatImageViewSet)
router.register(r'favorites', views.CatFavoriteViewSet, basename='favorites')

# URL patterns for the Cat API
urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Web interface
    path('', views.cat_home, name='cat-home'),
    path('breeds/', views.cat_breeds, name='cat-breeds'),
    path('breeds/<str:breed_id>/', views.cat_breed_detail, name='cat-breed-detail'),
    path('favorites/', views.cat_favorites, name='cat-favorites'),
]