# pokemon_api/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django import forms
from .models import Pokemon, APIRequest
from .services import PokemonAPIService
import json


class PokemonSearchForm(forms.Form):
    pokemon_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Pokemon name (e.g., pikachu, charizard)',
            'required': True
        })
    )


class PokemonListView(ListView):
    """View to display all Pokemon in database"""
    model = Pokemon
    template_name = 'pokemon_api/pokemon_list.html'
    context_object_name = 'pokemons'
    paginate_by = 20


class PokemonDetailView(DetailView):
    """View to display detailed Pokemon information"""
    model = Pokemon
    template_name = 'pokemon_api/pokemon_detail.html'
    context_object_name = 'pokemon'


class PokemonSearchView(FormView):
    """View to search and fetch Pokemon from API"""
    template_name = 'pokemon_api/pokemon_search.html'
    form_class = PokemonSearchForm
    success_url = reverse_lazy('pokemon_api:search')
    
    def form_valid(self, form):
        pokemon_name = form.cleaned_data['pokemon_name']
        service = PokemonAPIService()
        
        pokemon, success, error = service.fetch_pokemon(pokemon_name)
        
        if success:
            messages.success(
                self.request, 
                f"Successfully fetched data for {pokemon.name}!"
            )
            # Redirect to detail view
            self.success_url = reverse_lazy('pokemon_api:detail', kwargs={'pk': pokemon.pk})
        else:
            messages.error(self.request, f"Error: {error}")
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_requests'] = APIRequest.objects.all()[:10]
        return context


class PokemonAPIView(View):
    """API endpoint to fetch Pokemon data"""
    
    def get(self, request, pokemon_name):
        """Get Pokemon data (from database or fetch from API)"""
        try:
            # First try to get from database
            pokemon = Pokemon.objects.get(name=pokemon_name.lower())
            return JsonResponse({
                'success': True,
                'data': {
                    'id': pokemon.pokemon_id,
                    'name': pokemon.name,
                    'height': pokemon.height,
                    'weight': pokemon.weight,
                    'height_meters': pokemon.height_in_meters,
                    'weight_kg': pokemon.weight_in_kg,
                    'base_experience': pokemon.base_experience,
                    'types': pokemon.types,
                    'abilities': pokemon.abilities,
                    'hidden_abilities': pokemon.hidden_abilities,
                    'base_stats': pokemon.base_stats,
                }
            })
        except Pokemon.DoesNotExist:
            # If not in database, fetch from API
            service = PokemonAPIService()
            pokemon, success, error = service.fetch_pokemon(pokemon_name)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'data': {
                        'id': pokemon.pokemon_id,
                        'name': pokemon.name,
                        'height': pokemon.height,
                        'weight': pokemon.weight,
                        'height_meters': pokemon.height_in_meters,
                        'weight_kg': pokemon.weight_in_kg,
                        'base_experience': pokemon.base_experience,
                        'types': pokemon.types,
                        'abilities': pokemon.abilities,
                        'hidden_abilities': pokemon.hidden_abilities,
                        'base_stats': pokemon.base_stats,
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': error
                }, status=404 if 'not found' in error else 500)


class DownloadJSONView(View):
    """Download Pokemon data as JSON file"""
    
    def get(self, request, pk):
        pokemon = get_object_or_404(Pokemon, pk=pk)
        
        response = HttpResponse(
            json.dumps(pokemon.raw_data, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="{pokemon.name}_data.json"'
        return response
