# pokemon_api/apps.py
from django.apps import AppConfig


class PokemonApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pokemon_api'
    verbose_name = 'Pokemon API'
