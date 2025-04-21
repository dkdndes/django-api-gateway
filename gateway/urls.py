from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import JsonResponse
from . import views

# API router
router = DefaultRouter()
router.register(r'domains', views.DomainViewSet)
router.register(r'endpoints', views.ApiEndpointViewSet)
router.register(r'request-transformations', views.RequestTransformationViewSet)
router.register(r'response-transformations', views.ResponseTransformationViewSet)
router.register(r'logs', views.ApiLogViewSet)

app_name = 'gateway'

def health_check(request):
    """
    Simple health check endpoint that returns a 200 OK response.
    """
    return JsonResponse({
        'status': 'ok',
        'version': '0.1.1',
        'service': 'api-gateway'
    })

urlpatterns = [
    # API endpoints
    path('api/v1/', include(router.urls)),
    
    # Health check endpoint
    path('health/', health_check, name='health_check'),
    
    # Web interface
    path('', views.dashboard, name='dashboard'),
    path('rules/', views.rules_list, name='rules'),
    path('rules/create/', views.create_rule, name='create_rule'),
    path('rules/<int:endpoint_id>/edit/', views.edit_rule, name='edit_rule'),
    path('rules/<int:endpoint_id>/toggle/', views.toggle_rule, name='toggle_rule'),
    path('rules/<int:endpoint_id>/delete/', views.delete_rule, name='delete_rule'),
    path('logs/', views.logs_list, name='logs'),
    path('logs/clear/', views.clear_logs, name='clear_logs'),
    
    # AJAX endpoints
    path('ajax/create-domain/', views.create_domain_ajax, name='create_domain_ajax'),
    path('ajax/log-detail/', views.log_detail_ajax, name='log_detail_ajax'),
]