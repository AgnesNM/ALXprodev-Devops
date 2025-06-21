# pokemon_api/admin.py
from django.contrib import admin
from .models import Pokemon, APIRequest


@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    list_display = ['name', 'pokemon_id', 'height', 'weight', 'base_experience', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'pokemon_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'pokemon_id', 'height', 'weight', 'base_experience')
        }),
        ('Raw Data', {
            'fields': ('raw_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(APIRequest)
class APIRequestAdmin(admin.ModelAdmin):
    list_display = ['pokemon_name', 'success', 'http_status_code', 'request_timestamp']
    list_filter = ['success', 'request_timestamp', 'http_status_code']
    search_fields = ['pokemon_name', 'error_message']
    readonly_fields = ['request_timestamp']
    
    def has_add_permission(self, request):
        return False  # Don't allow manual creation

