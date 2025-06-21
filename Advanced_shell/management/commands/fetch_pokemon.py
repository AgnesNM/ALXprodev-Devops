# pokemon_api/management/commands/fetch_pokemon.py
from django.core.management.base import BaseCommand
from pokemon_api.services import PokemonAPIService


class Command(BaseCommand):
    help = 'Fetch Pokemon data from the API'
    
    def add_arguments(self, parser):
        parser.add_argument('pokemon_names', nargs='+', type=str, help='Pokemon names to fetch')
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force refetch even if Pokemon exists in database'
        )
    
    def handle(self, *args, **options):
        service = PokemonAPIService()
        
        for pokemon_name in options['pokemon_names']:
            self.stdout.write(f"Fetching {pokemon_name}...")
            
            pokemon, success, error = service.fetch_pokemon(pokemon_name)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Successfully fetched {pokemon.name}")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Failed to fetch {pokemon_name}: {error}")
                )


