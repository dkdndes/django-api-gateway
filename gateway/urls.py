from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'domains', views.DomainViewSet)
router.register(r'endpoints', views.ApiEndpointViewSet)
router.register(r'request-transformations', views.RequestTransformationViewSet)
router.register(r'response-transformations', views.ResponseTransformationViewSet)
router.register(r'logs', views.ApiLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]