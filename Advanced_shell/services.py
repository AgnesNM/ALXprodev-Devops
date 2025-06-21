# pokemon_api/services.py
import requests
import json
import logging
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from .models import Pokemon, APIRequest

logger = logging.getLogger(__name__)


class PokemonAPIService:
    """Service class to handle Pokemon API interactions"""
    
    BASE_URL = "https://pokeapi.co/api/v2/pokemon/"
    TIMEOUT = 30
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Django-Pokemon-App/1.0'
        })
    
    def fetch_pokemon(self, pokemon_name):
        """
        Fetch Pokemon data from API and save to database
        Returns: (Pokemon instance or None, success boolean, error message)
        """
        pokemon_name = pokemon_name.lower().strip()
        url = f"{self.BASE_URL}{pokemon_name}/"
        
        try:
            logger.info(f"Fetching Pokemon data for: {pokemon_name}")
            response = self.session.get(url, timeout=self.TIMEOUT)
            
            # Log the API request
            api_request = APIRequest.objects.create(
                pokemon_name=pokemon_name,
                success=response.status_code == 200,
                http_status_code=response.status_code,
                error_message="" if response.status_code == 200 else f"HTTP {response.status_code}",
                response_data=response.json() if response.status_code == 200 else None
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Save JSON data to file
                self._save_json_to_file(data, pokemon_name)
                
                # Create or update Pokemon in database
                pokemon, created = Pokemon.objects.update_or_create(
                    pokemon_id=data['id'],
                    defaults={
                        'name': data['name'],
                        'height': data['height'],
                        'weight': data['weight'],
                        'base_experience': data.get('base_experience'),
                        'raw_data': data
                    }
                )
                
                action = "Created" if created else "Updated"
                logger.info(f"{action} Pokemon: {pokemon.name}")
                
                return pokemon, True, None
                
            elif response.status_code == 404:
                error_msg = f"Pokemon '{pokemon_name}' not found"
                logger.warning(error_msg)
                return None, False, error_msg
                
            else:
                error_msg = f"API request failed with status {response.status_code}"
                logger.error(error_msg)
                return None, False, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = f"Request timeout for Pokemon: {pokemon_name}"
            logger.error(error_msg)
            self._log_error(pokemon_name, error_msg)
            return None, False, error_msg
            
        except requests.exceptions.ConnectionError:
            error_msg = f"Connection error when fetching Pokemon: {pokemon_name}"
            logger.error(error_msg)
            self._log_error(pokemon_name, error_msg)
            return None, False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            self._log_error(pokemon_name, error_msg)
            return None, False, error_msg
    
    def _save_json_to_file(self, data, pokemon_name):
        """Save JSON data to media/pokemon_data/ directory"""
        try:
            filename = f"pokemon_data/{pokemon_name}_{data['id']}.json"
            json_content = json.dumps(data, indent=2)
            
            # Save using Django's file storage system
            default_storage.save(filename, ContentFile(json_content))
            logger.info(f"Saved JSON data to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save JSON file: {str(e)}")
    
    def _log_error(self, pokemon_name, error_message):
        """Log error to database"""
        APIRequest.objects.create(
            pokemon_name=pokemon_name,
            success=False,
            error_message=error_message
        )
