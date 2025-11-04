# In odds/views.py

from django.shortcuts import render
from django.utils import timezone
from .models import Game

def odds_list_view(request):
    """
    Fetches all games that haven't happened yet
    and displays them on the page.
    """
    # Get all games where the game_time is in the future
    upcoming_games = Game.objects.filter(
        game_time__gte=timezone.now()
    ).order_by('game_time') # Show the soonest game first
    
    context = {
        'games': upcoming_games,
    }
    
    return render(request, 'odds/odds_list.html', context)