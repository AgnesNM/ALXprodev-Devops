# pokemon_api/urls.py
from django.urls import path
from . import views

app_name = 'pokemon_api'

urlpatterns = [
    path('', views.PokemonListView.as_view(), name='list'),
    path('search/', views.PokemonSearchView.as_view(), name='search'),
    path('pokemon/<int:pk>/', views.PokemonDetailView.as_view(), name='detail'),
    path('pokemon/<int:pk>/download/', views.DownloadJSONView.as_view(), name='download'),
    path('api/pokemon/<str:pokemon_name>/', views.PokemonAPIView.as_view(), name='api'),
]
