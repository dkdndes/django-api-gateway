from django.contrib import admin
from .models import Domain, ApiEndpoint, RequestTransformation, ResponseTransformation, ApiLog

class RequestTransformationInline(admin.TabularInline):
    model = RequestTransformation
    extra = 1

class ResponseTransformationInline(admin.TabularInline):
    model = ResponseTransformation
    extra = 1

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_url', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'base_url', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ApiEndpoint)
class ApiEndpointAdmin(admin.ModelAdmin):
    list_display = ('domain', 'method', 'path', 'target_url', 'is_active', 'created_at', 'updated_at')
    list_filter = ('domain', 'method', 'is_active')
    search_fields = ('domain__name', 'path', 'target_url')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [RequestTransformationInline, ResponseTransformationInline]

@admin.register(RequestTransformation)
class RequestTransformationAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'source_field', 'target_field', 'transformation_type', 'is_active')
    list_filter = ('endpoint__domain', 'transformation_type', 'is_active')
    search_fields = ('endpoint__domain__name', 'endpoint__path', 'source_field', 'target_field')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ResponseTransformation)
class ResponseTransformationAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'source_field', 'target_field', 'transformation_type', 'is_active')
    list_filter = ('endpoint__domain', 'transformation_type', 'is_active')
    search_fields = ('endpoint__domain__name', 'endpoint__path', 'source_field', 'target_field')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ApiLog)
class ApiLogAdmin(admin.ModelAdmin):
    list_display = ('request_method', 'request_path', 'response_status', 'execution_time', 'created_at')
    list_filter = ('request_method', 'response_status')
    search_fields = ('request_path', 'request_body', 'response_body')
    readonly_fields = ('endpoint', 'request_method', 'request_path', 'request_headers', 
                      'request_body', 'response_status', 'response_headers', 
                      'response_body', 'execution_time', 'created_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
